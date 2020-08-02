-- region 1. trigger : un-publish the product once it is modified
-- trigger function for product update --> unpublish product
create function "product_update_procedure"() returns trigger as
$product_update_procedure$
begin
    update "product" set new."published" = false where "id" = new."id";
    return new;
end
$product_update_procedure$ LANGUAGE plpgsql;

create trigger check_product_states
    after update
    on "product"
execute procedure product_update_procedure();
-- endregion
