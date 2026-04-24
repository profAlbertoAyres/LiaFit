SPECIAL_MENU_ROUTES: dict[tuple[str, str], str] = {
    # ---- Dashboards ----
    ("core",       "dashboard"): "master:dashboard",
    ("my-area",    "dashboard"): "master:dashboard",
    ("saas-admin", "dashboard"): "master:dashboard",

    # ---- Detalhe único (não tem list) ----
    ("account", "organization"): "tenant:organization_detail",  # ⬅️ MUDOU

    # ---- SaaS Admin ----
    ("saas-admin", "organizations"): "master:organizations",
    ("saas-admin", "users"):         "master:users",
    ("saas-admin", "billing"):       "master:billing",

    # ---- My Area ----
    ("my-area", "organizations"): "master:my_organizations",
    ("my-area", "profile"):       "master:my_profile",
}
