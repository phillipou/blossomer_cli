# Bug Tracking

## Open Bugs

### BUG-001: Keyboard shortcuts (c/e/a) not working in questionary.select menus
**Priority:** Medium  
**Status:** Open  
**Date Reported:** 2025-07-16  
**Description:** 
- User reports that keyboard shortcuts 'c', 'e', 'a' are not working in the preview menus during GTM generation flow
- Only arrow keys work to navigate the questionary.select menus
- Expected behavior: Pressing 'c' should select "Continue", 'e' should select "Edit", 'a' should select "Abort"

**Steps to Reproduce:**
1. Run `blossomer init <domain>`
2. Wait for target account generation to complete
3. When preview menu appears with [C]ontinue/[E]dit/[A]bort options
4. Try pressing 'c', 'e', or 'a' keys
5. Keys don't register - only arrow keys work

**Technical Details:**
- Attempted fix using `questionary.Choice()` with `shortcut_key` parameter but it was reverted by linter/formatter
- Current implementation uses basic questionary.select() without shortcut support
- Need to investigate questionary version compatibility or alternative implementation

**Workaround:** 
Use arrow keys to navigate and Enter to select

**Next Steps:**
- Investigate questionary documentation for proper shortcut implementation
- Test with different questionary versions
- Consider alternative UI library if questionary shortcuts are incompatible
- Ensure any fix doesn't get reverted by code formatting tools

## Closed Bugs

_(None yet)_