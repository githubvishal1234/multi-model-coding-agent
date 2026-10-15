"""Entry point: load every service and build its listing."""

from services import orders, billing, shipping, customers, catalog, reviews, coupons, returns, warehouse, suppliers, reports, notifications, analytics, search, pricing, accounts, audit, exports


def run_all(raw):
    """raw: dict service name -> list of raw records. Returns listings per service."""
    out = {}
    out["orders"] = orders.list_orders(orders.create_orders(raw.get("orders", [])))
    out["billing"] = billing.list_billing(billing.create_billing(raw.get("billing", [])))
    out["shipping"] = shipping.list_shipping(shipping.create_shipping(raw.get("shipping", [])))
    out["customers"] = customers.list_customers(customers.create_customers(raw.get("customers", [])))
    out["catalog"] = catalog.list_catalog(catalog.create_catalog(raw.get("catalog", [])))
    out["reviews"] = reviews.list_reviews(reviews.create_reviews(raw.get("reviews", [])))
    out["coupons"] = coupons.list_coupons(coupons.create_coupons(raw.get("coupons", [])))
    out["returns"] = returns.list_returns(returns.create_returns(raw.get("returns", [])))
    out["warehouse"] = warehouse.list_warehouse(warehouse.create_warehouse(raw.get("warehouse", [])))
    out["suppliers"] = suppliers.list_suppliers(suppliers.create_suppliers(raw.get("suppliers", [])))
    out["reports"] = reports.list_reports(reports.create_reports(raw.get("reports", [])))
    out["notifications"] = notifications.list_notifications(notifications.create_notifications(raw.get("notifications", [])))
    out["analytics"] = analytics.list_analytics(analytics.create_analytics(raw.get("analytics", [])))
    out["search"] = search.list_search(search.create_search(raw.get("search", [])))
    out["pricing"] = pricing.list_pricing(pricing.create_pricing(raw.get("pricing", [])))
    out["accounts"] = accounts.list_accounts(accounts.create_accounts(raw.get("accounts", [])))
    out["audit"] = audit.list_audit(audit.create_audit(raw.get("audit", [])))
    out["exports"] = exports.list_exports(exports.create_exports(raw.get("exports", [])))
    return out
