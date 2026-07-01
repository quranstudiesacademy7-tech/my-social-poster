# Social Auto Poster — Setup Guide (Urdu)

Ye system automatically har roz aapke schedule ke mutabiq **Facebook Page** aur
**Instagram Business account** par AI se banai gayi image + caption post karta hai.
Hosting bilkul **FREE** hai (GitHub Actions ke zariye).

---

## Step 1: Instagram ko Business account banayein aur Facebook Page se link karein
1. Instagram app > Settings > Account > "Switch to Professional Account" > Business
2. Instagram ko apni Facebook Page se link karein (Settings > Linked Accounts)

## Step 2: Meta Developer App banayein
1. https://developers.facebook.com/ par jayein > "My Apps" > "Create App"
2. Type: **Business** select karein
3. App banne ke baad, "Add Product" mein se **Facebook Login** aur
   **Instagram Graph API** add karein

## Step 3: Access Tokens nikalein
1. https://developers.facebook.com/tools/explorer/ (Graph API Explorer) kholein
2. Apni app select karein, aur permissions add karein:
   `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`,
   `instagram_content_publish`, `business_management`
3. "Generate Access Token" par click karein aur login karein
4. Is short-lived token ko **long-lived Page Access Token** mein convert karein
   (Meta docs: "Access Tokens" > "Long-Lived Tokens" follow karein, ya humse
   is step par dobara madad lein)
5. Apna **Page ID** (Page Settings > About mein milta hai) aur
   **Instagram Business Account ID** (Graph API Explorer se: `me/accounts`
   query karke page ka `instagram_business_account.id` nikalein) note kar lein

## Step 4: GitHub par repo banayein
1. https://github.com par free account banayein (agar nahi hai)
2. Naya **public** repository banayein (public isliye taake GitHub Actions
   ki minutes bilkul free/unlimited milein)
3. Is folder (`social-auto-poster`) ki tamam files us repo mein upload kar dein
   (GitHub website par "Add file > Upload files" se bhi ho jata hai, coding
   ki zarurat nahi)

## Step 5: Secrets add karein (tokens ko surakshit rakhne ke liye)
Repo mein: **Settings > Secrets and variables > Actions > New repository secret**

Ye secrets add karein:
| Secret Name | Value |
|---|---|
| `FB_PAGE_ID` | Aapki Facebook Page ID |
| `FB_PAGE_ACCESS_TOKEN` | Long-lived Page Access Token |
| `IG_USER_ID` | Instagram Business Account ID |
| `IG_ACCESS_TOKEN` | (agar alag na ho to FB wala hi token daal dein) |
| `ANTHROPIC_API_KEY` | (optional — behtar AI captions ke liye) |

## Step 6: Schedule set karein
`schedule.json` file kholein aur apna 1 month ka plan likh dein:
- `topic`: post kis baare mein hai
- `image_prompt`: AI image kaisi banni chahiye (English mein likhein, behtar
  result milta hai)
- `caption`: agar khud caption dena chahain to yahan likh dein, warna khali
  chorden — AI khud bana dega

**Jab bhi schedule change karna ho**, bas is file ko GitHub par edit kar dein
(pencil icon se) — agli post automatically nayi schedule follow karegi.

**Agar aap agla month schedule na dein**, system apne aap **purana schedule
dobara se (loop) chalata rahega** — posting kabhi nahi rukegi.

## Step 7: Test karein
Repo ke **Actions** tab mein jayein > "Daily Social Media Post" workflow
select karein > "Run workflow" button se manually chala kar test kar lein.

Agar sab sahi hai to ye khud roz (jo time `daily_post.yml` mein set hai) chalta
rahega, bina kisi aur mehnat ke.

---

### Note
- Time zone: workflow file mein cron UTC time mein hai. Pakistan time (PKT)
  UTC+5 hai, is hisaab se time adjust kar lein.
- Agar Facebook/Instagram API mein koi error aaye, "Actions" tab mein log
  check karein — usually token expire ya permission missing hoti hai.
