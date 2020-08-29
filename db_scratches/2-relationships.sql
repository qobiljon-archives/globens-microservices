-- region vacancy relationships
-- 1.vacancy <-> user relationship : many to zero
-- 2. vacancy <-> business page relationship (business page owner vacancy) : many to one
alter table "gb_vacancy"
    add column "user_id"          integer references "gb_user" ("id") default null,
    add column "business_page_id" integer references "gb_business_page" ("id") on delete cascade;
-- endregion


-- region vacancy application relationships
-- 3. vacancy_application <-> user relationship : many to one
-- 4. vacancy_application <-> vacancy relationship : many to one
alter table "gb_vacancy_application"
    add column "user_id"    integer references "gb_user" ("id") on delete cascade,
    add column "vacancy_id" integer references "gb_vacancy" ("id") on delete cascade;
-- endregion


-- region 5. business page <-> product relationship : zero to many
alter table "gb_product"
    add column "business_page_id" integer references "gb_business_page" ("id") on delete cascade;
-- endregion


-- region 6. purchase <-> product relationship : zero to one
alter table "gb_purchase"
    add column "product_id" integer references "gb_product" ("id") on delete cascade;
-- endregion


-- region 7. purchase <-> user relationship : zero to one
alter table "gb_purchase"
    add column "buyer_id" integer references "gb_user" ("id") on delete set null;
-- endregion
