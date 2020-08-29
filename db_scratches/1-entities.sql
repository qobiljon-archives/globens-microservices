-- region 1. platform entity --> consumer or producer
create table if not exists "gb_user"
(
    "id"          serial primary key,
    "email"       text unique,
    "name"        varchar(300),
    "picture"     text,
    "pictureBlob" bytea,
    "tokens"      text,
    "sessionKey"  varchar(300) default null
);
-- endregion


-- region 2. vacancy --> users create/occupy vacancy in business page
-- role type for vacancy --> business owner, employee, or individual entrepreneur
create type "gb_vacancy_role" as enum ('business owner', 'employee', 'individual entrepreneur');
create table if not exists "gb_vacancy"
(
    "id"    serial primary key,
    "role"  gb_vacancy_role,
    "title" varchar(250) -- todo check 250 character length for our vacancies
);
-- endregion


-- region 3. vacancy_applications --> users apply for a vacancy
create table if not exists "gb_vacancy_application"
(
    "id" serial primary key
);
-- endregion


-- region 4. business page for creating/publishing products
-- business page for creating/publishing products
create type "gb_business_page_type" as enum ('small business', 'large business');
create table if not exists "gb_business_page"
(
    "id"          serial primary key,
    "type"        gb_business_page_type,
    "title"       text,
    "pictureBlob" bytea
);
-- endregion


-- region 5. product : platform entity
create table if not exists "gb_product"
(
    "id"        serial primary key,
    "name"      varchar(250), -- todo check 250 character length for our products
    "published" boolean default false
);
-- endregion


-- region 6. log of purchases --> consumer buys a product from producer
create table if not exists "gb_purchase"
(
    "id"            serial primary key,
    "purchase_time" timestamp
);
-- endregion


--  region 7. others

-- endregion
