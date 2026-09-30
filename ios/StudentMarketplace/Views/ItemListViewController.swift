import UIKit

/// Displays the list of marketplace items in a UITableView.
class ItemListViewController: UITableViewController {

    private var items: [Item] = []
    private var selectedCategory: String? // nil = "All"

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Marketplace"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "ItemCell")

        // "+" button to create a new item
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(openCreateItem)
        )
        
        loadCategories()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadItems()
    }

    // MARK: - Data loading

    private func loadItems() {
        let requestedCategory = selectedCategory

        APIClient.getItems(category: requestedCategory) { [weak self] result in
            DispatchQueue.main.async {
                guard let self, requestedCategory == self.selectedCategory else { return }

                switch result {
                case .success(let items):
                    self.items = items
                    self.tableView.reloadData()
                case .failure(let error):
                    let alert = UIAlertController(
                        title: "Error",
                        message: error.localizedDescription,
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "OK", style: .default))
                    self.present(alert, animated: true)
                }
            }
        }
    }
    
    private func loadCategories() {
        APIClient.getCategories { [weak self] result in
            DispatchQueue.main.async {
                guard case .success(let categories) = result, !categories.isEmpty else { return }
                
                let row = CategoryChipRowView(frame: .zero)
                row.setCategories(categories)
                row.onCategorySelected = { [weak self] category in
                    self?.selectedCategory = category
                    self?.loadItems()
                }
                self?.tableView.tableHeaderView = row
            }
        }
    }

    // MARK: - UITableViewDataSource

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        items.count
    }

    override func tableView(_ tableView: UITableView,
                            cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ItemCell", for: indexPath)
        let item = items[indexPath.row]

        var config = cell.defaultContentConfiguration()
        config.text = item.title
        config.secondaryText = "\(item.formattedPrice) — \(item.category)"
        if item.isSold {
            config.secondaryText = "[SOLD] \(config.secondaryText ?? "")"
        }
        cell.contentConfiguration = config
        cell.accessoryType = .disclosureIndicator
        cell.alpha = item.isSold ? 0.5 : 1.0
        return cell
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        guard let header = tableView.tableHeaderView else { return }

        let size = header.systemLayoutSizeFitting(
            CGSize(width: tableView.bounds.width, height: UIView.layoutFittingCompressedSize.height),
            withHorizontalFittingPriority: .required,
            verticalFittingPriority: .fittingSizeLevel
        )
        if header.frame.height != size.height {
            header.frame.size.height = size.height
            tableView.tableHeaderView = header // re-assign so the table picks up the new height
        }
    }
    
    // MARK: - UITableViewDelegate

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let item = items[indexPath.row]
        let detailVC = ItemDetailViewController()
        detailVC.itemId = item.id
        navigationController?.pushViewController(detailVC, animated: true)
    }

    // MARK: - Actions

    @objc private func openCreateItem() {
        let createVC = CreateItemViewController()
        navigationController?.pushViewController(createVC, animated: true)
    }
}
