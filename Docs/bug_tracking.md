# Bug Tracking

# Polish Needed
-[] Instea of just "Analyzing with AI...", can we have a central place where I can define an array of string where we can cycle through different loading state text every 3 seconds? Each step in our cli (overview, account, persona, etc. should get it's own array). Every second we add a "." so it'll look like "Text."->"Text.."->"Text..."->"Text2." -> "Text2.." etc assuming our states array if [Text, Text2]. we'll remain at "Text2."->"Text2..","Text2..." assuming the animation takes longer than the length of the array, we'll just nimate the ...'s in the last string.
-[] Update "Continue to next step
    -[] After overview: "Next: Target Accounts"
    -[] After account: "Next: Target Personas"
    -[] After persona: "Next: Email Campaign"
    -[] After email: "Next: Create GTM plan"
-[] Update "Edit < > in editor" -> just have it say "Edit <STEP>.md" (e.g. "Edit overview.md", "Edit persona.md", etc.)
-[] Institute 40s timeouts for all operations
-[x] instead of strategic_plan.md, let's save it as strategy.md
-[x] "→ View full plan: Open gtm_projects/https://stripe.com/plans/strategic_plan.md → Edit plan: gtm_projects/https://stripe.com/plans/strategic_plan.md" is what we see after GTM strategic plan is completed. Instead, we should just simply tell users "View your full plan in plans/strategy.md" to avoid making it seem like we're askin them to navigate to a website.
