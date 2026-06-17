# Technical Design: Gmail OAuth Integration

This document outlines the architectural decisions and security considerations implemented in the Gmail OAuth integration project.

## 🏗 System Architecture
The application follows the Django **Model-View-Template (MVT)** pattern, utilizing a stateful session-based approach to handle OAuth 2.0 flows.

### 1. The OAuth 2.0 Flow (with PKCE)
To ensure security, the application implements the **Proof Key for Code Exchange (PKCE)** extension for OAuth 2.0. This prevents authorization code injection attacks.
*   **Initialization:** The `google_login` view generates a `code_verifier` and a corresponding `code_challenge`.
*   **State Management:** The `code_verifier` is stored in the Django session, ensuring the same client that initiated the request completes it.
*   **Token Exchange:** Upon callback, the application validates the `state` parameter to prevent CSRF and exchanges the authorization code for an access token using the verified `code_verifier`.

### 2. Gmail API Integration
*   **Client Initialization:** The project uses the `googleapiclient.discovery` library to build a service object, which abstracts the RESTful nature of the Gmail API into a Pythonic interface.
*   **Resource Management:** The `google_callback` view handles the token exchange and immediately utilizes the `service.users().messages().list()` method to fetch inbox identifiers.
*   **Data Parsing:** The application iterates through message IDs, performing granular `get` requests to extract the `payload` headers (From/Subject) and `snippet`.

### 3. Session & Security
*   **Secure Session Handling:** Uses Django’s `SessionMiddleware` to persist OAuth states and verifiers across HTTP redirects.
*   **Security Notice:** The `OAUTHLIB_INSECURE_TRANSPORT` flag is currently set to `1` to facilitate local development over HTTP. 
    *   *Implementation Note:* In a production environment, this flag must be removed, and the application must be served over HTTPS to ensure tokens are not intercepted in transit.

## 🧩 Component Interaction
| Component | Responsibility |
| :--- | :--- |
| **`views.py`** | Orchestrates the OAuth flow and API service communication. |
| **`sessions`** | Manages `oauth_state` and `oauth_code_verifier` across redirects. |
| **`emails.html`** | Renders the parsed email metadata using Django's template engine. |
| **`credentials.json`** | Stores client secrets (excluded from version control). |

## 🚀 Scalability Considerations
*   **Token Refresh:** The current implementation uses an `offline` access type, which provides a `refresh_token`. The architecture is prepared to handle token expiration by re-fetching access tokens without re-prompting the user.
*   **API Throttling:** The current implementation fetches the 5 most recent emails. For larger datasets, implementing a background task queue (like Celery) would be recommended to prevent blocking the request/response cycle.
