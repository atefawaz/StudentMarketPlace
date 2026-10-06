//
//  Session.swift
//  StudentMarketplace
//
//  Created by Atef Fawaz on 04/10/2026.
//

import Foundation
final class Session {
    static let shared = Session()
    private init() {}
    
    private(set) var currentSeller : Seller?
    
    var isLoggedIn: Bool {
        currentSeller != nil
    }
    
    
    func login(username: String, password: String,
               completion: @escaping (Result<Seller, Error>) -> Void) {

        APIClient.login(username: username, password: password) { [weak self] result in
            switch result {
            case .success(let token):
                KeychainStore.save(token)              //  storing the token
                self?.fetchCurrentSeller(completion: completion)   //  get the user
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    /// Shared by login and restore: calls /auth/me and stores the seller.
    private func fetchCurrentSeller(completion: @escaping (Result<Seller, Error>) -> Void) {
        APIClient.me { [weak self] result in
            switch result {
            case .success(let seller):
                self?.currentSeller = seller
                DispatchQueue.main.async {
                    NotificationCenter.default.post(name: .sessionChanged, object: nil)
                }
                completion(.success(seller))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    
    
    func register(username: String, password: String,
                  displayName: String, email: String,
                  completion: @escaping (Result<Seller, Error>) -> Void) {

        APIClient.register(username: username, password: password,
                           displayName: displayName, email: email) { result in
            switch result {
            case .success(let seller):
                completion(.success(seller))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    
    func restore(completion: ((Bool) -> Void)? = nil) {
        guard KeychainStore.read() != nil else {
            completion?(false)        // no saved token → nobody to restore
            return
        }

        fetchCurrentSeller { result in
            switch result {
            case .success:
                completion?(true)     // token was valid, seller loaded
            case .failure:
                completion?(false)    // token was invalid/expired (401 already cleared it)
            }
        }
    }
    
    func logout() {
        KeychainStore.delete()      
        currentSeller = nil
        NotificationCenter.default.post(name: .sessionChanged, object: nil)
    }
}
