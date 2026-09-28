# iOS Setup Instructions

## Prerequisites

- macOS with Xcode 15+ installed
- Python backend running on `localhost:5000`

## Getting Started

1. **Open the project in Xcode:**
   - Open Xcode and select **Create a new Xcode project**.
   - Choose **App** under the iOS tab.
   - Set Product Name to `StudentMarketplace`, Interface to **Storyboard**, Language to **Swift**.
   - Save the project inside the `ios/` directory.

2. **Add the source files:**
   - Drag the `StudentMarketplace/Models`, `StudentMarketplace/Services`, and `StudentMarketplace/Views` folders into your Xcode project navigator.
   - Make sure "Copy items if needed" is **unchecked** (files are already in place).
   - Make sure "Create folder references" is selected.

3. **Replace the default `Info.plist`:**
   - The provided `Info.plist` already allows HTTP connections to `localhost`.
   - Copy it over the auto-generated one, or merge the `NSAppTransportSecurity` key.

4. **Set the root view controller:**
   - In `SceneDelegate.swift` (or `AppDelegate.swift` if not using scenes), set:
     ```swift
     let nav = UINavigationController(rootViewController: ItemListViewController())
     window?.rootViewController = nav
     ```

5. **Run the backend first:**
   ```bash
   cd backend
   python seed.py
   uvicorn app:app --reload --port 5000
   ```

6. **Run the app** on the iOS Simulator (iPhone 15 recommended).

## Architecture

```
Models/
  Item.swift          — Codable data model
Services/
  APIClient.swift     — URLSession HTTP client
Views/
  ItemListViewController.swift    — Table view listing items
  ItemDetailViewController.swift  — Detail screen (TODO)
  CreateItemViewController.swift  — Create form (TODO)
```

## Notes

- The iOS Simulator can reach `localhost` directly (no special IP needed).
- If you run on a physical device, change `APIClient.baseURL` to your Mac's local IP.
