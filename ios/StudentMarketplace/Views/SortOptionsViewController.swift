import UIKit

final class SortOptionsViewController: UITableViewController {
    
    private let selectedOption: ItemSortOption
    private let onSelect: (ItemSortOption) -> Void
    
    // MARK: - Factory
    
    static func makeSheet(selectedOption: ItemSortOption, onSelect: @escaping (ItemSortOption) -> Void) -> UIViewController {
        let content = SortOptionsViewController(selectedOption: selectedOption, onSelect: onSelect)
        let navigationController = UINavigationController(rootViewController: content)
        
        if let sheet = navigationController.sheetPresentationController {
            sheet.detents = [.medium()]
            sheet.prefersGrabberVisible = true
            sheet.prefersEdgeAttachedInCompactHeight = true
        }
        
        return navigationController
    }
    
    // MARK: - Init
    
    private init(selectedOption: ItemSortOption, onSelect: @escaping (ItemSortOption) -> Void) {
        self.selectedOption = selectedOption
        self.onSelect = onSelect
        super.init(style: .insetGrouped)
    }
    
    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Sort by"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "SortCell")
        
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .close,
            target: self,
            action: #selector(closeTapped)
        )
    }
    
    // MARK: - UITableViewDataSource
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        ItemSortOption.allCases.count
    }
    
    override func tableView(_ tableView: UITableView,
                                cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "SortCell", for: indexPath)
        let option = ItemSortOption.allCases[indexPath.row]
 
        var config = cell.defaultContentConfiguration()
        config.text = option.title
        cell.contentConfiguration = config
        cell.accessoryType = (option == selectedOption) ? .checkmark : .none
        return cell
    }
 
    // MARK: - UITableViewDelegate
 
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let option = ItemSortOption.allCases[indexPath.row]
 
        if option != selectedOption {
            onSelect(option)
        }
        dismiss(animated: true)
    }
 
    // MARK: - Actions
 
    @objc private func closeTapped() {
        dismiss(animated: true)
    }
}
