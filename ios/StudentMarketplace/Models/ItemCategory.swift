enum ItemCategoryOptions: String, CaseIterable {
    case electronics = "Electronics"
    case clothing = "Clothing"
    case furniture = "Furniture"
    case toys = "Toys"
    case books = "Books"
    case other = "Other"
}

struct ItemCategory: Codable, Identifiable {
    let name: String
    let itemCount: Int

    var id: String {
        name
    }

    enum CodingKeys: String, CodingKey {
        case name = "category_name"
        case itemCount = "category_count"
    }
}
