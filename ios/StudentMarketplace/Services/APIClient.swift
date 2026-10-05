import Foundation

/// Minimal HTTP client for the Student Marketplace backend.
///
/// Uses URLSession — no third-party dependencies needed.
///
///
///


extension Notification.Name {
    static let sessionExpired = Notification.Name("sessionExpired")
    static let sessionChanged = Notification.Name("sessionChanged")
}

enum APIError : LocalizedError{
    case notFound
    case forbidden
    case unauthorized
    case server(Int)
    
    var errorDescription: String? {
        switch self {
        case .notFound :    return "This item no longer exists "
        case .forbidden : return "You don't have permission to do this."
        case .unauthorized : return "Your session has expired. Please log in again."
        case .server(let s) : return "Service error (\(s))."
            
        }
    }
}
class APIClient {

    /// Base URL of the FastAPI server.
    /// Change to your machine's IP if running on a physical device.
    static let baseURL = "http://127.0.0.1:5000"
    
    
    
    /// Inspects an HTTP response and returns the body data, or the right APIError.
    private static func handle(data: Data?, response: URLResponse?, error: Error?) -> Result<Data, Error> {
        if let error = error { return .failure(error) }

        guard let http = response as? HTTPURLResponse else {
            return .failure(URLError(.badServerResponse))
        }

        switch http.statusCode {
        case 200...299:
            guard let data = data else { return .failure(URLError(.badServerResponse)) }
            return .success(data)
        case 401:
            KeychainStore.delete()
            NotificationCenter.default.post(name: .sessionExpired, object: nil)
            return .failure(APIError.unauthorized)
        case 403:
            return .failure(APIError.forbidden)
        case 404:
            return .failure(APIError.notFound)
        default:
            return .failure(APIError.server(http.statusCode))
        }
    }

    /// Adds the Authorization: Bearer header if a token is stored.
    private static func authorize(_ request: inout URLRequest) {
        if let token = KeychainStore.read() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
    }

    // MARK: - GET /items

    /// Fetch marketplace items, optionally filtered by category.
    static func getItems(category: String? = nil,
                         order_by: String? = nil,
                         completion: @escaping (Result<[Item], Error>) -> Void) {
        guard var components = URLComponents(string: "\(baseURL)/items") else {
            completion(.failure(URLError(.badURL)))
            return
        }

        var queryItems: [URLQueryItem] = []
        
        if let category { queryItems.append(URLQueryItem(name: "category", value: category)) }
        if let order_by { queryItems.append(URLQueryItem(name: "sort", value: order_by)) }
        
        components.queryItems = queryItems.isEmpty ? nil : queryItems

        guard let url = components.url else {
            completion(.failure(URLError(.badURL)))
            return
        }
        
        var request = URLRequest(url: url)
                request.cachePolicy = .reloadIgnoringLocalCacheData

        URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else {
                completion(.failure(URLError(.badServerResponse)))
                return
            }
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
        authorize(&urlRequest)
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
    
    
    /// Mark an item as sold or available.
    static func setSold(id: Int, isSold: Bool,
                        completion: @escaping (Result<Item, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/items/\(id)") else { return }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "PATCH"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        authorize(&urlRequest)
        urlRequest.httpBody = try? JSONEncoder().encode(["is_sold": isSold])

        URLSession.shared.dataTask(with: urlRequest) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

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
    
    // MARK: - GET /categories
    
    static func getCategories(completion: @escaping (Result<[ItemCategory], Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/categories") else { return }
        
        URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else { return }
            do {
                let categories = try JSONDecoder().decode([ItemCategory].self, from: data)
                completion(.success(categories))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    
    
    
    
    // MARK: - POST /auth/login
    static func login(username: String, password: String,
                      completion: @escaping (Result<String, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/auth/login") else {
            completion(.failure(URLError(.badURL))); return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONEncoder().encode(["username": username, "password": password])

        URLSession.shared.dataTask(with: request) { data, response, error in
            switch handle(data: data, response: response, error: error) {
            case .success(let data):
                do { completion(.success(try JSONDecoder().decode(TokenResponse.self, from: data).accessToken)) }
                catch { completion(.failure(error)) }
            case .failure(let error): completion(.failure(error))
            }
        }.resume()
    }

    // MARK: - POST /auth/register
    static func register(username: String, password: String,
                         displayName: String, email: String,
                         completion: @escaping (Result<Seller, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/auth/register") else {
            completion(.failure(URLError(.badURL))); return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONEncoder().encode([
            "username": username, "password": password,
            "display_name": displayName, "email": email
        ])

        URLSession.shared.dataTask(with: request) { data, response, error in
            switch handle(data: data, response: response, error: error) {
            case .success(let data):
                do { completion(.success(try JSONDecoder().decode(Seller.self, from: data))) }
                catch { completion(.failure(error)) }
            case .failure(let error): completion(.failure(error))
            }
        }.resume()
    }

    // MARK: - GET /auth/me  (needs auth)
    static func me(completion: @escaping (Result<Seller, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/auth/me") else {
            completion(.failure(URLError(.badURL))); return
        }
        var request = URLRequest(url: url)
        authorize(&request)

        URLSession.shared.dataTask(with: request) { data, response, error in
            switch handle(data: data, response: response, error: error) {
            case .success(let data):
                do { completion(.success(try JSONDecoder().decode(Seller.self, from: data))) }
                catch { completion(.failure(error)) }
            case .failure(let error): completion(.failure(error))
            }
        }.resume()
    }
}
