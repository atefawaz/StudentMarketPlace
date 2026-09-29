import Foundation

/// Minimal HTTP client for the Student Marketplace backend.
///
/// Uses URLSession — no third-party dependencies needed.
///
///
///


enum APIError : LocalizedError{
    case notFound
    case server(Int)
    
    var errorDescription: String? {
        switch self {
        case .notFound :    return "This item no longer exists "
        case .server(let s) : return "Service error (\(s))."
            
        }
    }
}
class APIClient {

    /// Base URL of the FastAPI server.
    /// Change to your machine's IP if running on a physical device.
    static let baseURL = "http://127.0.0.1:5000"

    // MARK: - GET /items

    /// Fetch all marketplace items.
    static func getItems(completion: @escaping (Result<[Item], Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/items") else { return }

        URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else { return }
            do {
                let items = try JSONDecoder().decode([Item].self, from: data)
                completion(.success(items))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    // MARK: - GET /items/{id}

    /// Fetch a single item by its id.
    
    static func getItem(id: Int, completion: @escaping (Result<Item, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/items/\(id)") else { return }

        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            // SMKT-S005: look at the HTTP status code before decoding.
            if let http = response as? HTTPURLResponse {
                if http.statusCode == 404 {
                    completion(.failure(APIError.notFound))
                    return
                }
                if !(200...299).contains(http.statusCode) {
                    completion(.failure(APIError.server(http.statusCode)))
                    return
                }
            }

            guard let data = data else { return }
            do {
                let item = try JSONDecoder().decode(Item.self, from: data)
                completion(.success(item))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    // MARK: - POST /items

    /// Create a new item.
    static func createItem(_ request: CreateItemRequest,
                           completion: @escaping (Result<Item, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/items") else { return }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try? JSONEncoder().encode(request)

        URLSession.shared.dataTask(with: urlRequest) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else { return }
            do {
                let item = try JSONDecoder().decode(Item.self, from: data)
                completion(.success(item))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}
