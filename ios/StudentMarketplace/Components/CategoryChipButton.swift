import UIKit

final class CategoryChipButton: UIButton {
    
    init(title: String) {
        super.init(frame: .zero)
        
        var config = UIButton.Configuration.tinted()
        config.title = title
        config.cornerStyle = .capsule
        config.buttonSize = .small
        configuration = config
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
