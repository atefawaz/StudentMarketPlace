import UIKit

final class CategoryChipButton: UIButton {
    
    init(title: String) {
        super.init(frame: .zero)

        // Re-run by UIKit whenever isSelected (or any other state) changes.
        configurationUpdateHandler = { button in
            var config = button.isSelected ? UIButton.Configuration.filled() : UIButton.Configuration.tinted()
            config.title = title
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
