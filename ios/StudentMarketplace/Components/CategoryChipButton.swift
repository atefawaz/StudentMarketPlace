import UIKit

final class CategoryChipButton: UIButton {
    
    init(title: String, count: Int) {
        super.init(frame: .zero)
        
        let text = "\(title) (\(count.formatted()))"

        // Re-run by UIKit whenever isSelected (or any other state) changes.
        configurationUpdateHandler = { button in
            var config = button.isSelected ? UIButton.Configuration.filled() : UIButton.Configuration.tinted()
            config.title = text
            config.cornerStyle = .capsule
            config.buttonSize = .small
            button.configuration = config
        }
        setNeedsUpdateConfiguration()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
