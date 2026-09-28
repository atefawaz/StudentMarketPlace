import Foundation

/// Represents a marketplace item returned by the API.
struct Item: Codable, Identifiable {
    let id: Int
    let title: String
    let description: String?
    let price: Double
    let category: String
    let imageUrl: String?
    let sellerName: String
    let createdAt: String
    let isSold: Bool

    enum CodingKeys: String, CodingKey {
        case id, title, description, price, category
        case imageUrl = "image_url"
        case sellerName = "seller_name"
        case createdAt = "created_at"
        case isSold = "is_sold"
    }

    /// Price formatted for display (e.g. "12.50 EUR").
    var formattedPrice: String {
        String(format: "%.2f EUR", price)
    }
}

/// Used when creating a new item (POST body).
struct CreateItemRequest: Codable {
    let title: String
    let description: String?
    let price: Double
    let category: String
    let imageUrl: String?
    let sellerName: String

    enum CodingKeys: String, CodingKey {
        case title, description, price, category
        case imageUrl = "image_url"
        case sellerName = "seller_name"
    }
}
