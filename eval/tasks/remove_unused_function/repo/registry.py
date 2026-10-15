"""Report registry: report name -> summary function (looked up by name at runtime)."""

from services import orders, billing, shipping, customers, catalog, reviews, coupons, returns, warehouse, suppliers, reports, notifications, analytics, search, pricing, accounts, audit, exports

REPORTS = {
    "orders": orders.summarize_orders,
    "billing": billing.summarize_billing,
    "shipping": shipping.summarize_shipping,
    "customers": customers.summarize_customers,
    "catalog": catalog.summarize_catalog,
    "reviews": reviews.summarize_reviews,
    "coupons": coupons.summarize_coupons,
    "returns": returns.summarize_returns,
    "warehouse": warehouse.summarize_warehouse,
    "suppliers": suppliers.summarize_suppliers,
    "reports": reports.summarize_reports,
    "notifications": notifications.summarize_notifications,
    "analytics": analytics.summarize_analytics,
    "search": search.summarize_search,
    "pricing": pricing.summarize_pricing,
    "accounts": accounts.summarize_accounts,
    "audit": audit.summarize_audit,
    "exports": exports.summarize_exports,
}
