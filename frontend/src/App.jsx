import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [invoices, setInvoices] = useState([]);
  const [invoiceLoading, setInvoiceLoading] = useState(false);
  const [invoiceError, setInvoiceError] = useState("");

  // =========================================
  // INVOICE DETAILS
  // =========================================

  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");

  const viewInvoiceDetails = async (invoiceId) => {
    setSelectedInvoice(null);
    setDetailsLoading(true);
    setDetailsError("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/invoices/id/${invoiceId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load invoice details"
        );
      }

      setSelectedInvoice(data);
    } catch (err) {
      setDetailsError(err.message);
    } finally {
      setDetailsLoading(false);
    }
  };

  const closeInvoiceDetails = () => {
    setSelectedInvoice(null);
    setDetailsLoading(false);
    setDetailsError("");
  };

  // Close popup using Escape key
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        closeInvoiceDetails();
      }
    };

    if (
      selectedInvoice ||
      detailsLoading ||
      detailsError
    ) {
      window.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [selectedInvoice, detailsLoading, detailsError]);

  // =========================================
  // AUTHENTICATION
  // =========================================

  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("invoiceGuardUser");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [authMode, setAuthMode] = useState("login");

  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");
  const [authMessage, setAuthMessage] = useState("");

  const handleAuthSubmit = async (e) => {
    e.preventDefault();

    setAuthLoading(true);
    setAuthError("");
    setAuthMessage("");

    const endpoint =
      authMode === "login"
        ? "http://127.0.0.1:8000/login"
        : "http://127.0.0.1:8000/register";

    const body =
      authMode === "login"
        ? {
            email: authForm.email,
            password: authForm.password,
          }
        : authForm;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Authentication failed"
        );
      }

      if (authMode === "login") {
        setUser(data.user);

        localStorage.setItem(
          "invoiceGuardUser",
          JSON.stringify(data.user)
        );

        setAuthForm({
          name: "",
          email: "",
          password: "",
        });

        setPage("dashboard");
      } else {
        setAuthMessage(
          "Registration successful. You can now login."
        );

        setAuthMode("login");

        setAuthForm({
          name: "",
          email: authForm.email,
          password: "",
        });
      }
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("invoiceGuardUser");

    setUser(null);
    setInvoices([]);
    setResult(null);
    setFile(null);
    setPage("dashboard");

    setSelectedInvoice(null);
    setDetailsLoading(false);
    setDetailsError("");

    setAuthMode("login");

    setAuthForm({
      name: "",
      email: "",
      password: "",
    });

    setAuthError("");
    setAuthMessage("");
  };

  // =========================================
  // GET ALL INVOICES
  // =========================================

  const fetchInvoices = async () => {
    setInvoiceLoading(true);
    setInvoiceError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/invoices/"
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load invoices"
        );
      }

      setInvoices(data.invoices || []);
    } catch (err) {
      setInvoiceError(err.message);
    } finally {
      setInvoiceLoading(false);
    }
  };

  // =========================================
  // LOAD INVOICES WHEN APP STARTS
  // =========================================

  useEffect(() => {
    if (user) {
      fetchInvoices();
    }
  }, [user]);

  // =========================================
  // UPLOAD INVOICE
  // =========================================

  const uploadInvoice = async () => {
    if (!file) {
      setError("Please select an invoice file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/invoices/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to upload invoice"
        );
      }

      setResult(data);

      fetchInvoices();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =========================================
  // LOGIN / REGISTER PAGE
  // =========================================

  const renderAuthPage = () => {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-logo">
            <div className="logo-icon">IF</div>

            <div>
              <h1>InvoiceGuard</h1>
              <p>AI Fraud Detection</p>
            </div>
          </div>

          <div className="auth-heading">
            <h2>
              {authMode === "login"
                ? "Welcome Back"
                : "Create Account"}
            </h2>

            <p>
              {authMode === "login"
                ? "Login to continue to your invoice dashboard."
                : "Create an account to use InvoiceGuard."}
            </p>
          </div>

          <form
            className="auth-form"
            onSubmit={handleAuthSubmit}
          >
            {authMode === "register" && (
              <div className="auth-field">
                <label>Full Name</label>

                <input
                  type="text"
                  placeholder="Enter your name"
                  value={authForm.name}
                  onChange={(e) =>
                    setAuthForm({
                      ...authForm,
                      name: e.target.value,
                    })
                  }
                  required
                />
              </div>
            )}

            <div className="auth-field">
              <label>Email</label>

              <input
                type="email"
                placeholder="Enter your email"
                value={authForm.email}
                onChange={(e) =>
                  setAuthForm({
                    ...authForm,
                    email: e.target.value,
                  })
                }
                required
              />
            </div>

            <div className="auth-field">
              <label>Password</label>

              <input
                type="password"
                placeholder="Enter your password"
                value={authForm.password}
                onChange={(e) =>
                  setAuthForm({
                    ...authForm,
                    password: e.target.value,
                  })
                }
                required
              />
            </div>

            {authError && (
              <div className="auth-error">
                {authError}
              </div>
            )}

            {authMessage && (
              <div className="auth-success">
                {authMessage}
              </div>
            )}

            <button
              className="auth-button"
              type="submit"
              disabled={authLoading}
            >
              {authLoading
                ? "Please wait..."
                : authMode === "login"
                ? "Login"
                : "Create Account"}
            </button>
          </form>

          <div className="auth-switch">
            {authMode === "login" ? (
              <>
                <span>
                  Don't have an account?
                </span>

                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("register");
                    setAuthError("");
                    setAuthMessage("");
                  }}
                >
                  Register
                </button>
              </>
            ) : (
              <>
                <span>
                  Already have an account?
                </span>

                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setAuthError("");
                    setAuthMessage("");
                  }}
                >
                  Login
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  };

  // =========================================
  // DASHBOARD
  // =========================================

  const Dashboard = () => {
    const totalInvoices = invoices.length;

    const highRiskInvoices = invoices.filter(
      (invoice) =>
        invoice.risk_level === "HIGH"
    ).length;

    const mediumRiskInvoices = invoices.filter(
      (invoice) =>
        invoice.risk_level === "MEDIUM"
    ).length;

    const lowRiskInvoices = invoices.filter(
      (invoice) =>
        invoice.risk_level === "LOW"
    ).length;

    const fraudInvoices = invoices.filter(
      (invoice) =>
        invoice.fraud_detected
    ).length;

    return (
      <>
        <header className="header">
          <div>
            <h1>Invoice Dashboard</h1>

            <p>
              Welcome, {user?.name || "User"}. Analyze
              invoices and detect potential fraud.
            </p>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            Backend Connected
          </div>
        </header>

        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">▤</div>

            <div>
              <span>Total Invoices</span>
              <strong>{totalInvoices}</strong>
            </div>
          </div>

          <div className="stat-card high-risk">
            <div className="stat-icon">⚠</div>

            <div>
              <span>High Risk</span>
              <strong>{highRiskInvoices}</strong>
            </div>
          </div>

          <div className="stat-card medium-risk">
            <div className="stat-icon">!</div>

            <div>
              <span>Medium Risk</span>
              <strong>{mediumRiskInvoices}</strong>
            </div>
          </div>

          <div className="stat-card low-risk">
            <div className="stat-icon">✓</div>

            <div>
              <span>Low Risk</span>
              <strong>{lowRiskInvoices}</strong>
            </div>
          </div>

          <div className="stat-card fraud-detected">
            <div className="stat-icon">!</div>

            <div>
              <span>Fraud Detected</span>
              <strong>{fraudInvoices}</strong>
            </div>
          </div>
        </section>

        <section className="upload-card">
          <div className="upload-icon">
            ↑
          </div>

          <h2>Upload Invoice</h2>

          <p>
            Upload an invoice image for OCR analysis,
            fraud detection and ML prediction.
          </p>

          <label className="file-input">
            <input
              type="file"
              accept="image/*,.pdf"
              onChange={(e) => {
                setFile(e.target.files[0]);
                setError("");
              }}
            />

            <span>
              {file
                ? file.name
                : "Choose invoice file"}
            </span>
          </label>

          <button
            className="upload-button"
            onClick={uploadInvoice}
            disabled={loading}
            type="button"
          >
            {loading
              ? "Processing Invoice..."
              : "Analyze Invoice"}
          </button>

          {error && (
            <div className="error">
              {error}
            </div>
          )}
        </section>

        {result && (
          <section className="results">
            <div className="success-message">
              ✓ Invoice processed successfully
            </div>

            <div className="result-card">
              <h2>Invoice Information</h2>

              <div className="info-grid">
                <div>
                  <span>Invoice Number</span>

                  <strong>
                    {result.extracted_data.invoice_number ||
                      "Not available"}
                  </strong>
                </div>

                <div>
                  <span>Invoice Date</span>

                  <strong>
                    {result.extracted_data.invoice_date ||
                      "Not available"}
                  </strong>
                </div>

                <div>
                  <span>Vendor</span>

                  <strong>
                    {result.extracted_data.vendor_name ||
                      "Not available"}
                  </strong>
                </div>

                <div>
                  <span>Customer</span>

                  <strong>
                    {result.extracted_data.customer_name ||
                      "Not available"}
                  </strong>
                </div>

                <div>
                  <span>Subtotal</span>

                  <strong>
                    ₹
                    {result.extracted_data.subtotal?.toLocaleString() ||
                      "0"}
                  </strong>
                </div>

                <div>
                  <span>GST</span>

                  <strong>
                    ₹
                    {result.extracted_data.gst?.toLocaleString() ||
                      "0"}
                  </strong>
                </div>

                <div>
                  <span>Tax</span>

                  <strong>
                    ₹
                    {result.extracted_data.tax?.toLocaleString() ||
                      "0"}
                  </strong>
                </div>

                <div>
                  <span>Total Amount</span>

                  <strong className="total">
                    ₹
                    {result.extracted_data.total_amount?.toLocaleString() ||
                      "0"}
                  </strong>
                </div>
              </div>
            </div>

            <div className="analysis-grid">
              <div className="result-card">
                <h2>Rule-Based Analysis</h2>

                <div className="analysis-row">
                  <span>Risk Score</span>

                  <strong>
                    {result.fraud_analysis.risk_score}
                  </strong>
                </div>

                <div className="analysis-row">
                  <span>Risk Level</span>

                  <strong
                    className={
                      result.fraud_analysis.risk_level === "HIGH"
                        ? "danger"
                        : result.fraud_analysis.risk_level === "MEDIUM"
                        ? "warning"
                        : "safe"
                    }
                  >
                    {result.fraud_analysis.risk_level}
                  </strong>
                </div>

                <div className="analysis-row">
                  <span>Calculation Valid</span>

                  <strong>
                    {result.fraud_analysis.calculation_valid
                      ? "✓ Yes"
                      : "✕ No"}
                  </strong>
                </div>

                <div className="analysis-row">
                  <span>Duplicate</span>

                  <strong>
                    {result.fraud_analysis.duplicate
                      ? "⚠ Yes"
                      : "✓ No"}
                  </strong>
                </div>
              </div>

              <div className="result-card">
                <h2>ML Fraud Detection</h2>

                <div className="analysis-row">
                  <span>Prediction</span>

                  <strong
                    className={
                      result.ml_analysis.prediction === 1
                        ? "danger"
                        : "safe"
                    }
                  >
                    {result.ml_analysis.prediction === 1
                      ? "Fraudulent"
                      : "Genuine"}
                  </strong>
                </div>

                <div className="analysis-row">
                  <span>Fraud Probability</span>

                  <strong>
                    {(
                      result.ml_analysis.fraud_probability * 100
                    ).toFixed(1)}
                    %
                  </strong>
                </div>
              </div>
            </div>

            {result.fraud_analysis.problems?.length > 0 && (
              <div className="result-card problems">
                <h2>Detected Problems</h2>

                <ul>
                  {result.fraud_analysis.problems.map(
                    (problem, index) => (
                      <li key={index}>
                        ⚠ {problem}
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}
          </section>
        )}
      </>
    );
  };

  // =========================================
  // INVOICES PAGE
  // =========================================

  const InvoicesPage = () => {
    return (
      <>
        <header className="header">
          <div>
            <h1>Invoices</h1>

            <p>
              View all processed invoices
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchInvoices}
            type="button"
          >
            ↻ Refresh
          </button>
        </header>

        {invoiceLoading && (
          <div className="loading-box">
            Loading invoices...
          </div>
        )}

        {invoiceError && (
          <div className="error-box">
            {invoiceError}
          </div>
        )}

        {!invoiceLoading && !invoiceError && (
          <section className="table-card">
            <div className="table-header">
              <div>
                <h2>
                  Invoice Records
                </h2>

                <p>
                  Total invoices: {invoices.length}
                </p>
              </div>
            </div>

            {invoices.length === 0 ? (
              <div className="empty-state">
                No invoices found.
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Invoice Number</th>
                      <th>Vendor</th>
                      <th>Customer</th>
                      <th>Total</th>
                      <th>Risk Score</th>
                      <th>Risk Level</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {invoices.map((invoice) => (
                      <tr key={invoice.id}>
                        <td>
                          #{invoice.id}
                        </td>

                        <td>
                          {invoice.invoice_number ||
                            "Not available"}
                        </td>

                        <td>
                          {invoice.vendor_name ||
                            "Not available"}
                        </td>

                        <td>
                          {invoice.customer_name ||
                            "Not available"}
                        </td>

                        <td>
                          ₹
                          {invoice.total_amount
                            ? invoice.total_amount.toLocaleString()
                            : "0"}
                        </td>

                        <td>
                          {invoice.risk_score ?? "-"}
                        </td>

                        <td>
                          <span
                            className={`risk-badge ${
                              invoice.risk_level
                                ? invoice.risk_level.toLowerCase()
                                : "unknown"
                            }`}
                          >
                            {invoice.risk_level ||
                              "UNKNOWN"}
                          </span>
                        </td>

                        <td>
                          {invoice.fraud_detected ? (
                            <span className="fraud-status">
                              ⚠ Fraud
                            </span>
                          ) : (
                            <span className="genuine-status">
                              ✓ Genuine
                            </span>
                          )}
                        </td>

                        <td>
                          <button
                            className="view-button"
                            onClick={() =>
                              viewInvoiceDetails(invoice.id)
                            }
                            type="button"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </>
    );
  };

  // =========================================
  // FRAUD ALERTS PAGE
  // =========================================

  const FraudAlertsPage = () => {
    const suspiciousInvoices = invoices.filter(
      (invoice) =>
        invoice.risk_level === "HIGH" ||
        invoice.risk_level === "MEDIUM" ||
        invoice.fraud_detected === true
    );

    const highRiskCount = invoices.filter(
      (invoice) =>
        invoice.risk_level === "HIGH"
    ).length;

    const mediumRiskCount = invoices.filter(
      (invoice) =>
        invoice.risk_level === "MEDIUM"
    ).length;

    const fraudCount = invoices.filter(
      (invoice) =>
        invoice.fraud_detected === true
    ).length;

    return (
      <>
        <header className="header">
          <div>
            <h1>
              Fraud Alerts
            </h1>

            <p>
              Review invoices that require attention
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchInvoices}
            type="button"
          >
            ↻ Refresh
          </button>
        </header>

        <div className="alert-summary">
          <div className="alert-stat high-alert">
            <span>
              HIGH RISK
            </span>

            <strong>
              {highRiskCount}
            </strong>

            <small>
              Immediate attention
            </small>
          </div>

          <div className="alert-stat medium-alert">
            <span>
              MEDIUM RISK
            </span>

            <strong>
              {mediumRiskCount}
            </strong>

            <small>
              Needs review
            </small>
          </div>

          <div className="alert-stat fraud-alert">
            <span>
              FRAUD DETECTED
            </span>

            <strong>
              {fraudCount}
            </strong>

            <small>
              Flagged invoices
            </small>
          </div>

          <div className="alert-stat total-alert">
            <span>
              REQUIRES REVIEW
            </span>

            <strong>
              {suspiciousInvoices.length}
            </strong>

            <small>
              Total alerts
            </small>
          </div>
        </div>

        <section className="alerts-card">
          <div className="table-header">
            <div>
              <h2>
                Suspicious Invoices
              </h2>

              <p>
                Invoices with elevated fraud risk
              </p>
            </div>

            <span className="alert-count">
              {suspiciousInvoices.length} Alerts
            </span>
          </div>

          {suspiciousInvoices.length === 0 ? (
            <div className="empty-state">
              <div className="no-alert-icon">
                ✓
              </div>

              <h3>
                No Fraud Alerts
              </h3>

              <p>
                No suspicious invoices require attention.
              </p>
            </div>
          ) : (
            <div className="alert-list">
              {suspiciousInvoices.map(
                (invoice) => (
                  <div
                    className={`alert-item ${
                      invoice.risk_level
                        ? invoice.risk_level.toLowerCase()
                        : ""
                    }`}
                    key={invoice.id}
                  >
                    <div className="alert-icon">
                      ⚠
                    </div>

                    <div className="alert-info">
                      <div className="alert-title">
                        <strong>
                          {invoice.invoice_number ||
                            `Invoice #${invoice.id}`}
                        </strong>

                        <span
                          className={`risk-badge ${
                            invoice.risk_level
                              ? invoice.risk_level.toLowerCase()
                              : "unknown"
                          }`}
                        >
                          {invoice.risk_level ||
                            "UNKNOWN"}
                        </span>
                      </div>

                      <p>
                        {invoice.vendor_name ||
                          "Unknown Vendor"}
                      </p>

                      <span className="alert-details">
                        Invoice ID: #{invoice.id}
                        {" • "}
                        Amount: ₹
                        {invoice.total_amount
                          ? invoice.total_amount.toLocaleString()
                          : "0"}
                        {" • "}
                        Risk Score: {invoice.risk_score ?? "-"}
                      </span>
                    </div>

                    <div className="alert-actions">
                      <div className="alert-status">
                        {invoice.fraud_detected ? (
                          <span className="fraud-status">
                            ⚠ Fraud Detected
                          </span>
                        ) : (
                          <span className="review-status">
                            Review Required
                          </span>
                        )}
                      </div>

                      <button
                        className="alert-view-button"
                        onClick={() =>
                          viewInvoiceDetails(invoice.id)
                        }
                        type="button"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </section>
      </>
    );
  };

  // =========================================
  // SHARED INVOICE DETAILS MODAL
  // =========================================

  const InvoiceDetailsModal = () => {
    if (
      !selectedInvoice &&
      !detailsLoading &&
      !detailsError
    ) {
      return null;
    }

    // The details endpoint returns the database invoice together
    // with the extracted data and both analysis results.
    const invoice = selectedInvoice?.invoice || selectedInvoice;
    const extractedData = selectedInvoice?.extracted_data || {};
    const fraudAnalysis = selectedInvoice?.fraud_analysis || {};
    const mlAnalysis = selectedInvoice?.ml_analysis || {};

    // Prefer the detailed endpoint data and fall back to database fields.
    const invoiceNumber =
      extractedData.invoice_number ?? invoice?.invoice_number;
    const invoiceDate =
      extractedData.invoice_date ?? invoice?.invoice_date;
    const vendorName =
      extractedData.vendor_name ?? invoice?.vendor_name;
    const customerName =
      extractedData.customer_name ?? invoice?.customer_name;
    const gstin =
      extractedData.gstin ?? invoice?.gstin;
    const subtotal =
      extractedData.subtotal ?? invoice?.subtotal;
    const gst =
      extractedData.gst ?? invoice?.gst;
    const tax =
      extractedData.tax ?? invoice?.tax;
    const totalAmount =
      extractedData.total_amount ?? invoice?.total_amount;

    const riskScore =
      fraudAnalysis.risk_score ?? invoice?.risk_score;
    const riskLevel =
      fraudAnalysis.risk_level ?? invoice?.risk_level;
    const fraudDetected =
      fraudAnalysis.fraud_detected ?? invoice?.fraud_detected ?? false;
    const duplicate =
      fraudAnalysis.duplicate ?? invoice?.duplicate ?? false;
    const calculationValid =
      fraudAnalysis.calculation_valid;
    const problems =
      fraudAnalysis.problems || [];

    const mlPrediction =
      mlAnalysis.prediction ?? invoice?.ml_prediction;
    const mlProbability =
      mlAnalysis.fraud_probability ?? invoice?.ml_fraud_probability;

    const formatAmount = (value) => {
      if (value === null || value === undefined || value === "") {
        return "₹0";
      }
      const number = Number(value);
      return Number.isFinite(number)
        ? `₹${number.toLocaleString("en-IN")}`
        : `₹${value}`;
    };

    const formatGstin = (value) => {
      if (Array.isArray(value)) {
        return value.length ? value.join(", ") : "Not available";
      }
      return value || "Not available";
    };

    return (
      <div
        className="details-overlay"
        onClick={(event) => {
          if (event.target === event.currentTarget) {
            closeInvoiceDetails();
          }
        }}
      >
        <div
          className="details-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="invoice-details-title"
        >
          <div className="details-modal-header">
            <div className="details-header-title">
              <div className="details-header-icon">▤</div>
              <div>
                <span className="details-eyebrow">
                  INVOICE ANALYSIS
                </span>
                <h2 id="invoice-details-title">
                  Invoice Details
                </h2>
                <p>
                  {invoiceNumber || `Invoice #${invoice?.id || "-"}`}
                </p>
              </div>
            </div>

            <button
              className="details-close-button"
              onClick={closeInvoiceDetails}
              type="button"
              aria-label="Close invoice details"
            >
              ×
            </button>
          </div>

          {detailsLoading && (
            <div className="details-loading">
              <div className="details-loading-icon">⟳</div>
              <h3>Loading Invoice Details</h3>
              <p>
                Please wait while the invoice information is loaded.
              </p>
            </div>
          )}

          {detailsError && !detailsLoading && (
            <div className="details-error">
              <div className="details-error-icon">!</div>
              <h3>Unable to Load Invoice</h3>
              <p>{detailsError}</p>
              <button
                className="details-close-main-button"
                onClick={closeInvoiceDetails}
                type="button"
              >
                Close
              </button>
            </div>
          )}

          {invoice && !detailsLoading && !detailsError && (
            <div className="details-content">
              <div className="details-status-strip">
                <div>
                  <span>Analysis Status</span>
                  <strong
                    className={fraudDetected ? "danger" : "safe"}
                  >
                    {fraudDetected
                      ? "⚠ Fraud Detected"
                      : "✓ Genuine Invoice"}
                  </strong>
                </div>

                <div className="details-status-risk">
                  <span>Risk Level</span>
                  <strong
                    className={
                      riskLevel === "HIGH"
                        ? "danger"
                        : riskLevel === "MEDIUM"
                        ? "warning"
                        : "safe"
                    }
                  >
                    {riskLevel || "UNKNOWN"}
                  </strong>
                </div>
              </div>

              {/* BASIC INFORMATION */}
              <div className="details-section">
                <div className="details-section-heading">
                  <div className="details-section-number">01</div>
                  <div>
                    <h3>Invoice Information</h3>
                    <p>Extracted details from the uploaded invoice</p>
                  </div>
                </div>

                <div className="details-grid">
                  <div className="details-field">
                    <span>Invoice Number</span>
                    <strong>{invoiceNumber || "Not available"}</strong>
                  </div>

                  <div className="details-field">
                    <span>Invoice Date</span>
                    <strong>{invoiceDate || "Not available"}</strong>
                  </div>

                  <div className="details-field">
                    <span>Vendor</span>
                    <strong>{vendorName || "Not available"}</strong>
                  </div>

                  <div className="details-field">
                    <span>Customer</span>
                    <strong>{customerName || "Not available"}</strong>
                  </div>

                  <div className="details-field details-field-wide">
                    <span>GSTIN</span>
                    <strong>{formatGstin(gstin)}</strong>
                  </div>

                  <div className="details-field">
                    <span>Invoice ID</span>
                    <strong>#{invoice.id}</strong>
                  </div>
                </div>
              </div>

              {/* AMOUNT INFORMATION */}
              <div className="details-section">
                <div className="details-section-heading">
                  <div className="details-section-number">02</div>
                  <div>
                    <h3>Amount Information</h3>
                    <p>Financial values extracted from the invoice</p>
                  </div>
                </div>

                <div className="details-amount-grid">
                  <div className="details-amount-card">
                    <span>Subtotal</span>
                    <strong>{formatAmount(subtotal)}</strong>
                  </div>

                  <div className="details-amount-card">
                    <span>GST</span>
                    <strong>{formatAmount(gst)}</strong>
                  </div>

                  <div className="details-amount-card">
                    <span>Tax</span>
                    <strong>{formatAmount(tax)}</strong>
                  </div>

                  <div className="details-amount-card total-amount-card">
                    <span>Total Amount</span>
                    <strong>{formatAmount(totalAmount)}</strong>
                  </div>
                </div>
              </div>

              {/* FRAUD ANALYSIS */}
              <div className="details-section">
                <div className="details-section-heading">
                  <div className="details-section-number">03</div>
                  <div>
                    <h3>Fraud Analysis</h3>
                    <p>Rule-based validation and duplicate detection</p>
                  </div>
                </div>

                <div className="details-analysis-grid">
                  <div className="details-analysis-card">
                    <span>Risk Score</span>
                    <strong>{riskScore ?? "-"}</strong>
                    <small>out of 100</small>
                  </div>

                  <div className="details-analysis-card">
                    <span>Risk Level</span>
                    <strong
                      className={
                        riskLevel === "HIGH"
                          ? "danger"
                          : riskLevel === "MEDIUM"
                          ? "warning"
                          : "safe"
                      }
                    >
                      {riskLevel || "UNKNOWN"}
                    </strong>
                  </div>

                  <div className="details-analysis-card">
                    <span>Calculation Check</span>
                    <strong
                      className={
                        calculationValid === false
                          ? "danger"
                          : "safe"
                      }
                    >
                      {calculationValid === undefined
                        ? "Not available"
                        : calculationValid
                        ? "✓ Valid"
                        : "✕ Invalid"}
                    </strong>
                  </div>

                  <div className="details-analysis-card">
                    <span>Duplicate Check</span>
                    <strong className={duplicate ? "warning" : "safe"}>
                      {duplicate ? "⚠ Duplicate" : "✓ No Duplicate"}
                    </strong>
                  </div>
                </div>
              </div>

              {/* ML ANALYSIS */}
              <div className="details-section">
                <div className="details-section-heading">
                  <div className="details-section-number">04</div>
                  <div>
                    <h3>ML Fraud Detection</h3>
                    <p>Random Forest model prediction</p>
                  </div>
                </div>

                <div className="details-analysis-grid ml-grid">
                  <div className="details-analysis-card ml-prediction-card">
                    <span>ML Prediction</span>
                    <strong
                      className={
                        mlPrediction === 1 ? "danger" : "safe"
                      }
                    >
                      {mlPrediction === 1
                        ? "⚠ Fraudulent"
                        : mlPrediction === 0
                        ? "✓ Genuine"
                        : "Not available"}
                    </strong>
                  </div>

                  <div className="details-analysis-card probability-card">
                    <span>Fraud Probability</span>
                    <strong>
                      {mlProbability != null
                        ? `${(Number(mlProbability) * 100).toFixed(1)}%`
                        : "Not available"}
                    </strong>
                  </div>
                </div>
              </div>

              {/* DETECTED PROBLEMS */}
              {problems.length > 0 && (
                <div className="details-problems">
                  <div className="details-problems-title">
                    <div className="details-problem-icon">!</div>
                    <div>
                      <h3>Detected Problems</h3>
                      <p>Items that require attention</p>
                    </div>
                  </div>

                  <ul>
                    {problems.map((problem, index) => (
                      <li key={index}>{problem}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="details-footer">
                <button
                  className="details-close-main-button"
                  onClick={closeInvoiceDetails}
                  type="button"
                >
                  Close Details
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // =========================================
  // SHOW LOGIN PAGE
  // =========================================

  if (!user) {
    return renderAuthPage();
  }

  // =========================================
  // MAIN APPLICATION
  // =========================================

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">
            IF
          </div>

          <div>
            <h2>
              InvoiceGuard
            </h2>

            <p>
              AI Fraud Detection
            </p>
          </div>
        </div>

        <nav>
          <button
            className={`nav-item ${
              page === "dashboard"
                ? "active"
                : ""
            }`}
            onClick={() =>
              setPage("dashboard")
            }
            type="button"
          >
            <span>▣</span>
            Dashboard
          </button>

          <button
            className={`nav-item ${
              page === "invoices"
                ? "active"
                : ""
            }`}
            onClick={() =>
              setPage("invoices")
            }
            type="button"
          >
            <span>▤</span>
            Invoices
          </button>

          <button
            className={`nav-item ${
              page === "alerts"
                ? "active"
                : ""
            }`}
            onClick={() =>
              setPage("alerts")
            }
            type="button"
          >
            <span>⚠</span>
            Fraud Alerts
          </button>

          <button
            className="nav-item"
            onClick={() =>
              alert("Reports page coming soon")
            }
            type="button"
          >
            <span>▥</span>
            Reports
          </button>
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            {(user?.name || "U")
              .charAt(0)
              .toUpperCase()}
          </div>

          <div className="user-info">
            <strong>
              {user?.name || "User"}
            </strong>

            <span>
              {user?.email || ""}
            </span>
          </div>

          <button
            className="logout-button"
            onClick={logout}
            type="button"
          >
            Logout
          </button>
        </div>

        <div className="sidebar-bottom">
          <p>
            Intelligent Invoice
          </p>

          <p>
            Analysis System
          </p>
        </div>
      </aside>

      <main className="main">
        {page === "dashboard" && (
          <Dashboard />
        )}

        {page === "invoices" && (
          <InvoicesPage />
        )}

        {page === "alerts" && (
          <FraudAlertsPage />
        )}
      </main>

      {/* =========================================
          SHARED MODAL
          This is outside the individual pages.
          Therefore it works from Dashboard,
          Invoices and Fraud Alerts.
          ========================================= */}

      <InvoiceDetailsModal />
    </div>
  );
}

export default App;