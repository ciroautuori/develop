# Google OAuth Verification - Scope Justification

## Detailed Explanation for Requested Scopes

We have reviewed our application's scope usage and removed unused scopes (`gmail.readonly`, `gmail.compose`) and downgraded `calendar` to `calendar.events`.

Here is the detailed justification for the remaining required scopes:

### 1. Identify & Profile
*   **Scopes**: `email`, `profile`, `openid`
*   **Justification**: Required to authenticate the Admin user and associate their account with their Google Profile. We display the user's name and avatar in the dashboard header.

### 2. Google Analytics
*   **Scope**: `https://www.googleapis.com/auth/analytics.readonly`
*   **Feature**: "Website Traffic Dashboard"
*   **Justification**: Our application provides an analytics dashboard for the Admin. We need read-only access to fetch metrics like "Active Users", "Sessions", and "Bounce Rate" from the user's GA4 property to display them in a simplified view within our backoffice. We do not modify any analytics data.

### 3. Google Business Profile
*   **Scope**: `https://www.googleapis.com/auth/business.manage`
*   **Feature**: "Reputation Management & Posting"
*   **Justification**: The application allows the Admin to manage their business presence directly.
    *   **Reviews**: We need access to list and reply to customer reviews.
    *   **Posts**: We need access to publish "What's New" or "Offer" posts to their Business Profile.
    *   **Insights**: We fetch performance metrics (e.g., calls, website clicks) to display in the dashboard.

### 4. Google Search Console
*   **Scope**: `https://www.googleapis.com/auth/webmasters.readonly`
*   **Feature**: "SEO Performance Monitor"
*   **Justification**: The application monitors the SEO health of the user's website. We need read-only access to fetch "Top Queries", "Clicks", and "Impressions" data to show the user how their site is performing in Google Search, without them needing to access the Search Console natively.

### 5. Google Calendar
*   **Scope**: `https://www.googleapis.com/auth/calendar.events` (Downgraded from `calendar`)
*   **Feature**: "Automated Booking System"
*   **Justification**: When a customer books an appointment through our frontend, the application automatically creates a Google Meet event on the Admin's calendar.
    *   **Why we need it**: We need to *insert* new events (bookings) and *read* existing events (to check for conflicts/availability).
    *   **Why the narrow scope**: We swiched to `calendar.events` because we only need to manage events, not the entire calendar settings.

### 6. Gmail
*   **Scope**: `https://www.googleapis.com/auth/gmail.send` (Removed `readonly` and `compose`)
*   **Feature**: "Booking Confirmations & Quotes"
*   **Justification**: The application sends transactional emails on behalf of the Admin (e.g., "Booking Confirmed", "Here is your Quote").
    *   **Why we need it**: These emails must be sent from the user's own Gmail address to ensure high deliverability and trust with their direct clients.
    *   **Reduction**: We have removed `gmail.readonly` and `gmail.compose` as we only programmatically construct and send specific transactional messages. We do not read the user's inbox.

### 7. Google Drive & Docs
*   **Scopes**: `https://www.googleapis.com/auth/drive`, `https://www.googleapis.com/auth/documents`
*   **Feature**: "Quote Generator"
*   **Justification**: The application generates PDF quotes/invoices from a Google Doc template.
    *   **Process**: The app reads a specific "Quote Template" (Google Doc) chosen by the user, copies it, replaces placeholders (e.g., `{{CLIENT_NAME}}`) with actual data, and exports it as a PDF.
    *   **Drive Usage**: The generated PDF is then saved back to a specific "Preventivi" folder in the user's Drive so they have a copy of every quote sent.
    *   **Why `drive` file access is not enough**: We need to list files to find the template and create the output folder if it doesn't exist. We also need to copy the template which involves file creation.
