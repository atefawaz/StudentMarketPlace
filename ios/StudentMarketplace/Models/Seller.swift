//
//  Seller.swift
//  StudentMarketplace
//
//  Created by Atef Fawaz on 02/10/2026.
//

import Foundation

struct Seller: Codable {
    let id : Int
    let username : String
    let displayName : String
    let email : String
    let createdAt : String
    
    
    enum CodingKeys : String, CodingKey {
        case id , username , email
        case displayName = "display_name"
        case createdAt = "created_at"
    }
}

struct TokenResponse: Codable {
    let accessToken: String
    let tokenType: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
    }
}


