//
//  AuthViewController.swift
//  StudentMarketplace
//
//  Created by Atef Fawaz on 04/10/2026.
//

import UIKit

final class AuthViewController: UIViewController {

    // The two modes this one screen can be in.
    private enum Mode {
        case login
        case register
    }

    private var mode: Mode = .login

    // Toggle between Login / Register.
    private let modeControl = UISegmentedControl(items: ["Login", "Register"])

    // The input fields (FormTextField), kept as references so we can read their text.
    private let usernameField    = FormTextField(placeholder: "username")
    private let passwordField    = FormTextField(placeholder: "password")
    private let displayNameField = FormTextField(placeholder: "Your name")
    private let emailField       = FormTextField(placeholder: "you@epita.fr")

    // Each field wrapped in a FormFieldGroup (label + field + inline error).
    private lazy var usernameGroup    = FormFieldGroup(label: "Username", field: usernameField)
    private lazy var passwordGroup    = FormFieldGroup(label: "Password", field: passwordField)
    private lazy var displayNameGroup = FormFieldGroup(label: "Display name", field: displayNameField)
    private lazy var emailGroup       = FormFieldGroup(label: "Email", field: emailField)

    // The submit button ("Log In" / "Register").
    private let submitButton = UIButton(type: .system)

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Account"
        view.backgroundColor = .systemBackground
        setupUI()
    }

    private func setupUI() {
        modeControl.selectedSegmentIndex = 0

        submitButton.setTitle("Log In", for: .normal)
        submitButton.configuration = .borderedProminent()

        // Password fields shouldn't show the typed characters or autocorrect.
        passwordField.isSecureTextEntry = true
        usernameField.autocapitalizationType = .none
        usernameField.autocorrectionType = .no
        emailField.keyboardType = .emailAddress
        emailField.autocapitalizationType = .none
        emailField.autocorrectionType = .no

        let stack = UIStackView(arrangedSubviews: [
            modeControl,
            usernameGroup,
            passwordGroup,
            displayNameGroup,
            emailGroup,
            submitButton
        ])
        stack.axis = .vertical
        stack.spacing = 16
        stack.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(stack)

        let guide = view.safeAreaLayoutGuide
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: guide.topAnchor, constant: 24),
            stack.leadingAnchor.constraint(equalTo: guide.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: guide.trailingAnchor, constant: -20),
        ])

        modeControl.addTarget(self, action: #selector(modeChanged), for: .valueChanged)
        submitButton.addTarget(self, action: #selector(submitTapped), for: .touchUpInside)

        applyMode()
    }

    @objc private func modeChanged() {
        mode = modeControl.selectedSegmentIndex == 0 ? .login : .register
        applyMode()
    }

    private func applyMode() {
        let isRegister = (mode == .register)

        // Register-only fields: shown only in register mode.
        displayNameGroup.isHidden = !isRegister
        emailGroup.isHidden = !isRegister

        // Button title reflects the action.
        submitButton.setTitle(isRegister ? "Register" : "Log In", for: .normal)

        // Clear any stale errors when switching modes.
        [usernameGroup, passwordGroup, displayNameGroup, emailGroup].forEach {
            $0.errorMessage = nil
        }
    }

    @objc private func submitTapped() {
        // 1. Validate first. If anything's wrong, errors are shown and we stop.
        guard validate() else { return }

        // 2. Read the inputs.
        let username = usernameField.text ?? ""
        let password = passwordField.text ?? ""

        // 3. Prevent double-taps while the request is in flight.
        submitButton.isEnabled = false

        switch mode {
        case .login:
            Session.shared.login(username: username, password: password) { [weak self] result in
                DispatchQueue.main.async {
                    self?.handleAuthResult(result)
                }
            }

        case .register:
            let displayName = displayNameField.text ?? ""
            let email = emailField.text ?? ""

            Session.shared.register(username: username, password: password,
                                    displayName: displayName, email: email) { [weak self] result in
                DispatchQueue.main.async {
                    switch result {
                    case .success:
                        // Register succeeded but doesn't log in — so log in now (option a).
                        Session.shared.login(username: username, password: password) { loginResult in
                            DispatchQueue.main.async {
                                self?.handleAuthResult(loginResult)
                            }
                        }
                    case .failure(let error):
                        self?.submitButton.isEnabled = true
                        self?.handleRegisterError(error)
                    }
                }
            }
        }
    }

    /// Shared success/failure handling for a completed auth (login, or register→login).
    private func handleAuthResult(_ result: Result<Seller, Error>) {
        switch result {
        case .success:
            // Session is now updated (currentSeller set). Dismiss the screen.
            dismiss(animated: true)
        case .failure:
            submitButton.isEnabled = true
            // Generic error — don't reveal whether it was the username or password.
            passwordGroup.errorMessage = "Invalid username or password."
        }
    }

    /// Register-specific errors (e.g. 409 username taken).
    private func handleRegisterError(_ error: Error) {
        if let apiError = error as? APIError, case .server(409) = apiError {
            usernameGroup.errorMessage = "Username already taken."
        } else {
            usernameGroup.errorMessage = error.localizedDescription
        }
    }
    /// Validates the visible fields for the current mode.
    /// Returns true if everything is valid; sets inline errors otherwise.
    private func validate() -> Bool {
        var isValid = true

        let username = usernameField.text ?? ""
        let password = passwordField.text ?? ""

        // Username: required.
        if username.trimmingCharacters(in: .whitespaces).isEmpty {
            usernameGroup.errorMessage = "Username is required."
            isValid = false
        }

        // Password: at least 8 characters.
        if password.count < 8 {
            passwordGroup.errorMessage = "Password must be at least 8 characters."
            isValid = false
        }

        // Register-only fields.
        if mode == .register {
            let displayName = displayNameField.text ?? ""
            let email = emailField.text ?? ""

            if displayName.trimmingCharacters(in: .whitespaces).isEmpty {
                displayNameGroup.errorMessage = "Display name is required."
                isValid = false
            }
            if email.trimmingCharacters(in: .whitespaces).isEmpty {
                emailGroup.errorMessage = "Email is required."
                isValid = false
            }
        }

        return isValid
    }
    
}
