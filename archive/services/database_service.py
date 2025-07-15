"""
Database service layer for CRUD operations with Row-Level Security.

This module provides a centralized service layer for database operations
with proper user scoping and security controls.
"""

from contextlib import contextmanager
from typing import List, Optional, Any, Dict
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status

from app.models import Company, User, Account, Persona, Campaign
from app.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CompanyWithRelations,
    AccountWithRelations,
    PersonaWithRelations,
)


class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def _get_user(self, user_id: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @contextmanager
    def _set_user_context(self, user_id: str):
        """Temporarily sets the user ID for the current transaction."""
        try:
            self.db.execute(
                text("SET LOCAL app.current_user_id = :user_id"), {"user_id": user_id}
            )
            yield
        finally:
            self.db.execute(text("SET LOCAL app.current_user_id = ''"))

    def create_company(self, company_data: CompanyCreate, user_id: str) -> Company:
        """
        Creates a new company for a user, ensuring the user exists first.
        """
        print(f"DatabaseService: Creating company for user_id: {user_id}")
        # Ensure the user exists before creating the company
        self._get_user(user_id)

        db_company = Company(
            name=company_data.name,
            url=company_data.url,
            data=company_data.data,
            user_id=user_id,
        )
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        print(f"DatabaseService: Successfully created company with ID: {db_company.id}")
        return db_company

    def get_companies(self, user_id: str, skip: int, limit: int) -> List[Company]:
        """
        Gets all companies for a user.
        """
        with self._set_user_context(user_id):
            return (
                self.db.query(Company)
                .filter(Company.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .all()
            )

    def get_company(self, company_id: UUID, user_id: str) -> Company:
        """
        Gets a single company by ID, ensuring it belongs to the user.
        """
        with self._set_user_context(user_id):
            company = (
                self.db.query(Company)
                .filter(Company.id == company_id, Company.user_id == user_id)
                .first()
            )
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            return company

    def get_company_with_relations(
        self, company_id: UUID, user_id: str
    ) -> CompanyWithRelations:
        """
        Gets a company with its accounts, ensuring it belongs to the user.
        """
        with self._set_user_context(user_id):
            company = (
                self.db.query(Company)
                .filter(Company.id == company_id, Company.user_id == user_id)
                .first()
            )
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            return company

    def update_company(
        self, company_id: UUID, company_data: CompanyUpdate, user_id: str
    ) -> Company:
        """
        Updates a company's information.
        """
        company = self.get_company(
            company_id, user_id
        )  # Reuses get_company to enforce ownership
        update_data = company_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete_company(self, company_id: UUID, user_id: str):
        """
        Deletes a company and its related data.
        """
        company = self.get_company(
            company_id, user_id
        )  # Reuses get_company to enforce ownership
        self.db.delete(company)
        self.db.commit()

    def create_account(
        self, data: AccountCreate, company_id: UUID, user_id: str
    ) -> Account:
        """
        Creates a new account for a company.
        """
        # First, ensure the user has access to the parent company
        self.get_company(company_id, user_id)
        db_account = Account(**data.model_dump(), company_id=company_id)
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account

    def get_accounts(
        self, company_id: UUID, user_id: str, skip: int, limit: int
    ) -> List[Account]:
        """
        Gets all accounts for a company.
        """
        # Ensure user has access to the parent company
        self.get_company(company_id, user_id)
        return (
            self.db.query(Account)
            .filter(Account.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_account(self, account_id: UUID, user_id: str) -> Account:
        """
        Gets a single account by ID, ensuring it belongs to the user via company ownership.
        """
        print(f"🔍 [DEBUG] Getting account {account_id} for user {user_id}")
        account = (
            self.db.query(Account)
            .join(Company, Account.company_id == Company.id)
            .filter(Account.id == account_id, Company.user_id == user_id)
            .first()
        )
        if not account:
            print(f"❌ [DEBUG] Account {account_id} not found for user {user_id}")
            # Let's also check if the account exists without the user filter
            account_exists = self.db.query(Account).filter(Account.id == account_id).first()
            if account_exists:
                print(f"⚠️  [DEBUG] Account {account_id} exists but doesn't belong to user {user_id}")
                print(f"⚠️  [DEBUG] Account company_id: {account_exists.company_id}")
            else:
                print(f"⚠️  [DEBUG] Account {account_id} doesn't exist at all")
            raise HTTPException(status_code=404, detail="Account not found")
        print(f"✅ [DEBUG] Account {account_id} found for user {user_id}")
        return account

    def get_account_with_relations(
        self, account_id: UUID, user_id: str
    ) -> AccountWithRelations:
        """
        Gets an account with its personas, ensuring it belongs to the user.
        """
        account = self.get_account(account_id, user_id)
        return account

    def update_account(
        self, account_id: UUID, data: AccountUpdate, user_id: str
    ) -> Account:
        """
        Updates an account's information.
        """
        account = self.get_account(account_id, user_id)  # Enforce ownership
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(account, key, value)
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete_account(self, account_id: UUID, user_id: str):
        """
        Deletes an account.
        """
        account = self.get_account(account_id, user_id)  # Enforce ownership
        self.db.delete(account)
        self.db.commit()

    def create_persona(
        self, data: PersonaCreate, account_id: UUID, user_id: str
    ) -> Persona:
        """
        Creates a new persona for an account.
        """
        # Ensure user has access to the parent account
        self.get_account(account_id, user_id)
        db_persona = Persona(**data.model_dump(), account_id=account_id)
        self.db.add(db_persona)
        self.db.commit()
        self.db.refresh(db_persona)
        return db_persona

    def get_personas(
        self, account_id: UUID, user_id: str, skip: int, limit: int
    ) -> List[Persona]:
        """
        Gets all personas for an account.
        """
        # Ensure user has access to the parent account
        self.get_account(account_id, user_id)
        return (
            self.db.query(Persona)
            .filter(Persona.account_id == account_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_persona(self, persona_id: UUID, user_id: str) -> Persona:
        """
        Gets a single persona by ID, ensuring it belongs to the user.
        """
        persona = (
            self.db.query(Persona)
            .join(Account)
            .join(Company)
            .filter(Persona.id == persona_id, Company.user_id == user_id)
            .first()
        )
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        return persona

    def get_persona_with_relations(
        self, persona_id: UUID, user_id: str
    ) -> PersonaWithRelations:
        """
        Gets a persona with its campaigns, ensuring it belongs to the user.
        """
        persona = self.get_persona(persona_id, user_id)
        return persona

    def update_persona(
        self, persona_id: UUID, data: PersonaUpdate, user_id: str
    ) -> Persona:
        """
        Updates a persona's information.
        """
        persona = self.get_persona(persona_id, user_id)  # Enforce ownership
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(persona, key, value)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def delete_persona(self, persona_id: UUID, user_id: str):
        """
        Deletes a persona.
        """
        persona = self.get_persona(persona_id, user_id)  # Enforce ownership
        self.db.delete(persona)
        self.db.commit()

    def create_campaign(
        self,
        data: CampaignCreate,
        account_id: UUID,
        persona_id: UUID,
        user_id: str,
    ) -> Campaign:
        """
        Creates a new campaign for a persona.
        """
        # Ensure user has access to the parent persona
        self.get_persona(persona_id, user_id)
        db_campaign = Campaign(
            **data.model_dump(),
            account_id=account_id,
            persona_id=persona_id,
        )
        self.db.add(db_campaign)
        self.db.commit()
        self.db.refresh(db_campaign)
        return db_campaign

    def get_campaigns(
        self,
        account_id: UUID,
        user_id: str,
        persona_id: Optional[UUID],
        skip: int,
        limit: int,
    ) -> List[Campaign]:
        """
        Gets all campaigns for an account, optionally filtered by persona.
        """
        # Ensure user has access to the parent account
        self.get_account(account_id, user_id)
        query = self.db.query(Campaign).filter(Campaign.account_id == account_id)
        if persona_id:
            query = query.filter(Campaign.persona_id == persona_id)
        return query.offset(skip).limit(limit).all()

    def get_campaign(self, campaign_id: UUID, user_id: str) -> Campaign:
        """
        Gets a single campaign by ID, ensuring it belongs to the user.
        """
        campaign = (
            self.db.query(Campaign)
            .join(Account)
            .join(Company)
            .filter(Campaign.id == campaign_id, Company.user_id == user_id)
            .first()
        )
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign

    def update_campaign(
        self, campaign_id: UUID, data: CampaignUpdate, user_id: str
    ) -> Campaign:
        """
        Updates a campaign's information.
        """
        campaign = self.get_campaign(campaign_id, user_id)  # Enforce ownership
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def delete_campaign(self, campaign_id: UUID, user_id: str):
        """
        Deletes a campaign.
        """
        campaign = self.get_campaign(campaign_id, user_id)  # Enforce ownership
        self.db.delete(campaign)
        self.db.commit()
