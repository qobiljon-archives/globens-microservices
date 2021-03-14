-- region 1. trigger : un-publish the product once it is modified
-- trigger function for product update --> unpublish product
create or replace function "gb_product_update_procedure"() returns trigger as
$gb_product_update_procedure$
begin
    new."published" := false;
    return new;
end
$gb_product_update_procedure$ LANGUAGE plpgsql;

drop trigger if exists "gb_check_product_states" on "gb_product";
create trigger "gb_check_product_states"
    before update of "name", "productType", "pictureBlob", "price", "currency", "description", "content", "category_id", "business_page_id"
    on "gb_product"
    for each row
execute procedure "gb_product_update_procedure"();
-- endregion

-- region 2. trigger : user creation --> business page creation
create or replace function "gb_user_create_procedure"() returns trigger as
$gb_user_create_procedure$
declare
    userId             "gb_user"."id"%type;
    pictureBlob        "gb_user"."pictureBlob"%type;
    businessPageId     "gb_business_page"."id"%type;
    businessOwnerJobId "gb_job"."id"%type;
begin
    -- load new user's details for individual business page
    userId = new."id";
    pictureBlob = new."pictureBlob";

    -- create an individual/small business page
    insert into "gb_business_page"("title", "type", "pictureBlob")
    values (E'Individual entrepreneur\'s page', 'small business', pictureBlob)
    returning "id" into businessPageId;

    -- create business owner job position for the business page
    insert into gb_job("title", "role", "business_page_id")
    values ('Business owner', 'individual entrepreneur', businessPageId)
    returning "id" into businessOwnerJobId;

    -- map the user with the business owner vacancy (empty job position)
    update "gb_job" set "user_id" = userId where "id" = businessOwnerJobId;

    return new;
end
$gb_user_create_procedure$ language plpgsql;

drop trigger if exists "gb_check_user_creation" on "gb_user";
create trigger "gb_check_user_creation"
    after insert
    on "gb_user"
    for each row
execute procedure "gb_user_create_procedure"();
-- endregion

-- region 3. trigger : vacancy occupation --> vacancy applications removal
create or replace function "gb_remove_job_applications_procedure"() returns trigger as
$gb_remove_job_applications_procedure$
begin
    -- if the vacancy was occupied, remove the pending job applications
    if new."user_id" is not null
    then
        delete from "gb_job_application" where "job_id" = new."id";
    end if;
    return new;
end
$gb_remove_job_applications_procedure$ language plpgsql;

drop trigger if exists "gb_check_vacancy_occupation" on "gb_user";
create trigger "gb_check_vacancy_occupation"
    after update
    on "gb_job"
    for each row
execute procedure "gb_remove_job_applications_procedure"();
-- endregion

-- region 4. trigger : job application creation --> remove old one
create or replace function "gb_remove_old_job_application"() returns trigger as
$gb_remove_old_job_application$
begin
    -- remove old entry if exists
    delete from "gb_job_application" where "user_id" = new."user_id" and "job_id" = new."job_id";
    return new;
end
$gb_remove_old_job_application$ language plpgsql;

drop trigger if exists "gb_check_previous_job_application" on "gb_user";
create trigger "gb_check_previous_job_application"
    before insert
    on "gb_job_application"
    for each row
execute procedure "gb_remove_old_job_application"();
-- endregion

-- region 5. trigger : product review submission --> update stars
create or replace function "gb_update_product_stars"() returns trigger as
$gb_update_product_stars$
declare
    reviewsCount integer;
begin
    if (tg_op = 'INSERT') then
        update "gb_product" set "stars" = ("stars" * "reviewsCount" + new."stars") / ("reviewsCount" + 1), "reviewsCount" = "reviewsCount" + 1 where "id" = "new"."product_id";
        return new;
    elsif (tg_op = 'DELETE') then
        reviewsCount := (select count(*) from "gb_product_review" where "product_id" = old."product_id");
        if reviewsCount = 1 then
            update "gb_product" set "stars" = 0.0, "reviewsCount" = 0 where "id" = old."product_id";
        else
            update "gb_product" set "stars" = ("stars" * "reviewsCount" - old."stars") / ("reviewsCount" - 1), "reviewsCount" = "reviewsCount" - 1 where "id" = "old"."product_id";
        end if;
        return old;
    end if;
    return null;
end
$gb_update_product_stars$ language plpgsql;

drop trigger if exists "gb_recalculate_product_stars" on "gb_product_review";
create trigger "gb_recalculate_product_stars"
    before insert or delete
    on "gb_product_review"
    for each row
execute procedure "gb_update_product_stars"();
-- endregion
