-- region 1. trigger : un-publish the product once it is modified
-- trigger function for product update --> unpublish product
create function "gb_product_update_procedure"() returns trigger as
$gb_product_update_procedure$
begin
    update "gb_product" set new."published" = false where "id" = new."id";
    return new;
end
$gb_product_update_procedure$ LANGUAGE plpgsql;

create trigger gb_check_product_states
    after update
    on "gb_product"
execute procedure gb_product_update_procedure();
-- endregion
