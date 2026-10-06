import UIKit

/// Displays the list of marketplace items in a UITableView.
class ItemListViewController: UITableViewController {
    
    private var items: [Item] = []
    private var selectedCategory: String? // nil = "All"
    private var searchText: String? // nil or empty no search
    private var searchDebounce: Timer?
    private var selectedSort: ItemSortOption = .saved {
        didSet {
            ItemSortOption.saved = selectedSort
            updateSortButton()
        }
    }
    
    // MARK: - Pagination state
    private let pageSize = 5
    private let loadMoreThreshold = 5          // start loading when 5 rows from the end
    private var currentPage = 0
    private var hasNextPage = false
    private var isLoading = false
    
    private var requestGeneration = 0          // invalidates in-flight responses
    private var needsReload = false
    
    private enum FooterState { case hidden, loading, retry }
    private var footerState: FooterState = .hidden
    
    private lazy var sortButton: UIBarButtonItem = {
        let item = UIBarButtonItem(
            image: UIImage(systemName: "arrow.up.arrow.down.circle"),
            style: .plain,
            target: self,
            action: #selector(openSortSheet)
        )
        item.accessibilityLabel = "Sort"
        item.accessibilityValue = selectedSort.title
        return item
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Marketplace"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "ItemCell")
        
        // "+" button to create a new item
        let addButton = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(openCreateItem)
        )
        
        navigationItem.rightBarButtonItems = [addButton, sortButton]
        let search = UISearchController(searchResultsController: nil)
        search.searchResultsUpdater = self
        search.obscuresBackgroundDuringPresentation = false
        search.searchBar.placeholder = "Search items"
        navigationItem.searchController = search
        navigationItem.hidesSearchBarWhenScrolling = false
        
        updateSortButton()
        refreshAuthUI()
        
        NotificationCenter.default.addObserver(
            self, selector: #selector(sessionChanged),
            name: .sessionChanged, object: nil
        )
        NotificationCenter.default.addObserver(
            self, selector: #selector(sessionDidExpire),
            name: .sessionExpired, object: nil
        )
        NotificationCenter.default.addObserver(
            self, selector: #selector(itemDidUpdate(_:)),
            name: .itemUpdated, object: nil
        )
        
        refreshControl = UIRefreshControl()
        refreshControl?.addTarget(self, action: #selector(pullToRefresh), for: .valueChanged)
        
        loadCategories()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshAuthUI()
        if items.isEmpty || needsReload {
            needsReload = false
            reloadItems()
        }
    }
    
    
    private func refreshAuthUI() {
        // Ensure UI work always happens on the main thread, whoever called us.
        guard Thread.isMainThread else {
            DispatchQueue.main.async { [weak self] in self?.refreshAuthUI() }
            return
        }
        
        if let seller = Session.shared.currentSeller {
            navigationItem.leftBarButtonItem = UIBarButtonItem(
                title: "Log out",
                style: .plain,
                target: self,
                action: #selector(logoutTapped)
            )
            title = seller.username
        } else {
            navigationItem.leftBarButtonItem = UIBarButtonItem(
                title: "Log in",
                style: .plain,
                target: self,
                action: #selector(openAuth)
            )
            title = "Marketplace"
        }
    }
    
    // MARK: - Data loading
    
    /// Starts over from page 1 (category/sort change, pull-to-refresh, logout…).
    private func reloadItems() {
        requestGeneration += 1      // any in-flight response is now stale
        isLoading = false
        fetchPage(1)
    }
    
    private func loadNextPage() {
        guard hasNextPage, !isLoading else { return }
        fetchPage(currentPage + 1)
    }
    
    private func fetchPage(_ page: Int) {
        let generation = requestGeneration
        isLoading = true
        setFooter(page == 1 ? .hidden : .loading)
        
        APIClient.getItems(
            category: selectedCategory,
            order_by: selectedSort.rawValue,
            search : searchText,
            page: page,
            pageSize: pageSize
        ) { [weak self] result in
            DispatchQueue.main.async {
                guard let self, generation == self.requestGeneration else { return }
                self.isLoading = false
                self.refreshControl?.endRefreshing()
                
                switch result {
                case .success(let response):
                    self.currentPage = page
                    self.hasNextPage = response.hasNext
                    self.setFooter(.hidden)
                    if page == 1 {
                        self.items = response.items
                        self.tableView.reloadData()
                    } else {
                        self.appendItems(response.items)
                    }
                    
                case .failure(let error):
                    if page == 1 {
                        let alert = UIAlertController(
                            title: "Error",
                            message: error.localizedDescription,
                            preferredStyle: .alert
                        )
                        alert.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alert, animated: true)
                    } else {
                        self.setFooter(.retry)
                    }
                }
            }
        }
    }
    
    private func appendItems(_ newItems: [Item]) {
        // Offset pagination can repeat rows if items were added between requests.
        let existingIds = Set(items.map(\.id))
        let fresh = newItems.filter { !existingIds.contains($0.id) }
        guard !fresh.isEmpty else { return }
        
        let start = items.count
        items.append(contentsOf: fresh)
        let indexPaths = (start..<items.count).map { IndexPath(row: $0, section: 0) }
        tableView.insertRows(at: indexPaths, with: .none)
    }
    
    private func loadCategories() {
        APIClient.getCategories { [weak self] result in
            DispatchQueue.main.async {
                guard case .success(let categories) = result, !categories.isEmpty else { return }
                
                let row = CategoryChipRowView(frame: .zero)
                row.setCategories(categories)
                row.onCategorySelected = { [weak self] category in
                    self?.selectedCategory = category
                    self?.scrollToTop()
                    self?.reloadItems()
                }
                self?.tableView.tableHeaderView = row
            }
        }
    }
    
    // MARK: - Sorting
    
    private func updateSortButton() {
        sortButton.image = UIImage(systemName: "arrow.up.arrow.down.circle")
        sortButton.accessibilityValue = selectedSort.title
    }
    
    private func scrollToTop() {
        tableView.setContentOffset(CGPoint(x: 0, y: -tableView.adjustedContentInset.top),
                                   animated: false)
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
    
    override func tableView(_ tableView: UITableView,
                            willDisplay cell: UITableViewCell,
                            forRowAt indexPath: IndexPath) {
        guard hasNextPage, !isLoading, footerState != .retry,
              indexPath.row >= items.count - loadMoreThreshold else { return }
        
        // Hop out of the layout pass before touching the footer.
        DispatchQueue.main.async { [weak self] in self?.loadNextPage() }
    }
    
    // MARK: - Footer
    
    private func setFooter(_ state: FooterState) {
        footerState = state
        switch state {
        case .hidden:
            tableView.tableFooterView = nil
            
        case .loading:
            let spinner = UIActivityIndicatorView(style: .medium)
            spinner.frame = CGRect(x: 0, y: 0, width: tableView.bounds.width, height: 56)
            spinner.startAnimating()
            tableView.tableFooterView = spinner
            
        case .retry:
            var config = UIButton.Configuration.plain()
            config.title = "Couldn’t load more items. Tap to retry"
            config.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attrs in
                var attrs = attrs
                attrs.font = .preferredFont(forTextStyle: .footnote)
                return attrs
            }
            let button = UIButton(configuration: config, primaryAction: UIAction { [weak self] _ in
                self?.loadNextPage()
            })
            button.frame = CGRect(x: 0, y: 0, width: tableView.bounds.width, height: 56)
            tableView.tableFooterView = button
        }
    }
    
    // MARK: - Actions
    
    @objc private func openCreateItem() {
        
        // Gate: creating an item requires being logged in.
        guard Session.shared.currentSeller != nil else {
            openAuth()   // not logged in → show the auth screen instead
            return
        }
        
        needsReload = true
        let createVC = CreateItemViewController()
        navigationController?.pushViewController(createVC, animated: true)
    }
    
    @objc private func openAuth() {
        guard presentedViewController == nil else { return }
        let authVC = AuthViewController()
        let nav = UINavigationController(rootViewController: authVC)
        present(nav, animated: true)
    }
    
    @objc private func logoutTapped() {
        Session.shared.logout()
        refreshAuthUI()
        reloadItems()
    }
    
    @objc private func sessionChanged() {
        refreshAuthUI()
    }
    
    @objc private func sessionDidExpire() {
        refreshAuthUI()
        let alert = UIAlertController(
            title: "Session expired",
            message: "Please log in again.",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    @objc private func itemDidUpdate(_ notification: Notification) {
        guard let updated = notification.userInfo?["item"] as? Item,
              let row = items.firstIndex(where: { $0.id == updated.id }) else { return }
        items[row] = updated
        tableView.reloadRows(at: [IndexPath(row: row, section: 0)], with: .none)
    }
    
    @objc private func openSortSheet() {
        let sheet = SortOptionsViewController.makeSheet(selectedOption: selectedSort) { [weak self] option in
            guard let self else { return }
            self.selectedSort = option
            self.scrollToTop()
            self.reloadItems()
        }
        present(sheet, animated: true)
    }
    
    @objc private func pullToRefresh() {
        reloadItems()
    }
}
    
    extension ItemListViewController: UISearchResultsUpdating {
        func updateSearchResults(for searchController: UISearchController) {
            let text = searchController.searchBar.text?.trimmingCharacters(in: .whitespaces)

            // Debounce: cancel the previous pending search, schedule a new one.
            searchDebounce?.invalidate()
            searchDebounce = Timer.scheduledTimer(withTimeInterval: 0.3, repeats: false) { [weak self] _ in
                guard let self else { return }
                let newValue = (text?.isEmpty ?? true) ? nil : text
                guard newValue != self.searchText else { return }   
                self.searchText = newValue
                self.scrollToTop()
                self.reloadItems()
            }
        }
    }

