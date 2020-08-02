-- region 1.user <-> vacancy relationship : zero to many
alter table "user"
    add column "vacancy_id" integer references "vacancy" ("id") default null;
-- endregion


-- region 2. vacancy <-> business page relationship : many to one
alter table "business_page"
    add column "vacancy_id" integer references "vacancy" ("id");
-- endregion


-- region 3. vacancy_application <-> user relationship : many to one
alter table "vacancy_application"
    add column "user_id" integer references "user" ("id");
-- endregion


-- region 4. vacancy_application <-> vacancy relationship : many to one
alter table "vacancy_application"
    add column "vacancy_id" integer references "user" ("id");
-- endregion


-- region 5. business page <-> product relationship : zero to many
alter table "product"
    add column "business_page_id" integer references "business_page" ("id");
-- endregion


-- region 6. purchase <-> product relationship : zero to one
alter table "purchase"
    add column "product_id" integer references "product" ("id");
-- endregion


-- region 7. purchase <-> user relationship : zero to one
alter table "purchase"
    add column "buyer_id" integer references "user" ("id");
-- endregion
