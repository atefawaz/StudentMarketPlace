import Foundation

/// Sort orders supported by the `sort` query parameter of `GET /items`.
enum ItemSortOption: String, CaseIterable {
    case priceAscending  = "price_asc"
    case priceDescending = "price_desc"
    case dateDescending  = "date_desc"
    case dateAscending   = "date_asc"

    /// User-facing label. Order of cases above is the order shown in the sheet.
    var title: String {
        switch self {
        case .priceAscending:  return "Price: Low to High"
        case .priceDescending: return "Price: High to Low"
        case .dateDescending:  return "Date: Newest First"
        case .dateAscending:   return "Date: Oldest First"
        }
    }
    
    static let defaultOption: ItemSortOption = .dateDescending
}
