//
//  AppDelegate.swift
//  StudentMarketplace
//
//  Created by Ali Elrogbany on 28/09/2026.
//


import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

//        // ===== TEMPORARY auth test —
//        Session.shared.register(username: "testuser",
//                                password: "testpass123",
//                                displayName: "Test User",
//                                email: "test@epita.fr") { result in
//            switch result {
//            case .success(let seller):
//                print("✅ REGISTERED:", seller.username)
//
//                // now log in as the user we just created
//                Session.shared.login(username: "testuser", password: "testpass123") { loginResult in
//                    switch loginResult {
//                    case .success(let s):
//                        print("✅ LOGIN OK:", s.username, s.email)
//                    case .failure(let e):
//                        print("❌ LOGIN FAIL:", e.localizedDescription)
//                    }
//                }
//
//            case .failure(let error):
//                print("❌ REGISTER FAIL:", error.localizedDescription)
//            }
//        }
//        // ===== end temporary test =====

        return true
    }

    // MARK: UISceneSession Lifecycle

    func application(_ application: UIApplication,
                     configurationForConnecting connectingSceneSession: UISceneSession,
                     options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }
}
