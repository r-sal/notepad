import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [localError, setLocalError] = useState("");
  const { register, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLocalError("");
    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters");
      return;
    }
    if (password !== confirm) {
      setLocalError("Passwords do not match");
      return;
    }
    await register(email, password);
  };

  const displayError = localError || error;

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create account</h1>
        <p>Start organizing your notes</p>
        <form onSubmit={handleSubmit}>
          {displayError && <div className="auth-error">{displayError}</div>}
          <div className="form-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => { clearError(); setLocalError(""); setEmail(e.target.value); }}
              placeholder="you@example.com"
              required
              autoFocus
            />
          </div>
          <div className="form-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => { clearError(); setLocalError(""); setPassword(e.target.value); }}
              placeholder="At least 8 characters"
              required
            />
          </div>
          <div className="form-field">
            <label htmlFor="confirm">Confirm password</label>
            <input
              id="confirm"
              type="password"
              value={confirm}
              onChange={(e) => { clearError(); setLocalError(""); setConfirm(e.target.value); }}
              placeholder="Repeat your password"
              required
            />
          </div>
          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>
        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
