from django.urls import path
from . import views


urlpatterns = [
    path("adminlogin", views.adminlogin, name="adminlogin"),
    path("admin_change_password", views.admin_change_password, name="admin_change_password"),
    path("signout", views.signout, name="signout"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("productlist", views.productlist, name="productlist"),
    path("addproduct", views.addproduct, name="addproduct"),
    path("addproductgallery", views.addproductgallery, name="addproductgallery"),
    path("editproduct/<product_id>", views.editProduct, name="editproduct"),
    path("deleteproduct/<product_id>",views.deleteproduct,name="deleteproduct"),
    path("variationlist", views.variationlist, name="variationlist"),
    path("addvariation",views.addvariation,name='addvariation'),
    path("editvariation/<variation_id>", views.editvariation, name="editvariation"),
    path("deletevariation/<variation_id>",views.deletevariation,name="deletevariation"),
    path("categorylist/", views.categorylist, name="categorylist"),
    path("addcategory", views.addcategory, name="addcategory"),
    path("editcategory/<category_id>", views.editcategory, name="editcategory"),
    path("deletecategory/<category_id>",views.deletecategory,name="deletecategory"),
    path("activeorders", views.activeorders, name="activeorders"),
    path("admin_order_detail/<order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("order_history", views.order_history, name="order_history"),
    path("order_status_change/",views.order_status_change,name="order_status_change"),
    path("activeusers", views.activeusers, name="activeusers"),
    path("blockuser/<user_id>", views.blockuser, name="blockuser"),
    path("unblockuser/<user_id>", views.unblockuser, name="unblockuser"),
    path("deleteuser/<user_id>", views.deleteuser, name="deleteuser"),
    path("couponlist", views.couponlist, name="couponlist"),
    path("add_coupon", views.add_coupon, name="add_coupon"),
    path("editcoupon/<coupon_id>", views.editcoupon, name="editcoupon"),
    path("deletecoupon/<coupon_id>", views.deletecoupon, name="deletecoupon"),
    path("product_report", views.product_report, name="product_report"),
    path("sales_report", views.sales_report, name="sales_report"),
    path("product_export_csv",views.product_export_csv,name="product_export_csv"),
    path("product_export_pdf",views.product_export_pdf,name="product_export_pdf"),
    path("sales_export_csv", views.sales_export_csv, name="sales_export_csv"),
    path("sales_export_pdf", views.sales_export_pdf, name="sales_export_pdf"),
]



















   
    
    # path("brandlists", views.brandlists, name="brandlists"),
    
    
    # path("addbrand", views.addbrand, name="addbrand"),
   
    
   
    # path("editbrand/<brand_id>", views.editbrand, name="editbrand"),
    # path("deletebrand/<brand_id>", views.deletebrand, name="deletebrand"),
    
    
    
    
    # path("blockvarient/<varient_id>", views.blockvarient, name="blockvarient"),
    # path("unblockvarient/<varient_id>",views.unblockvarient,name="unblockvarient"),
    
    
   
    # path("add_brand_offer", views.add_brand_offer, name="add_brand_offer"),
    # path("existing_brand_Offer",views.existing_brand_Offer,name="existing_brand_Offer"),
    # path("add_category_offer",views.add_category_offer,name="add_category_offer"),
    # path("existing_category_Offer",views.existing_category_Offer,name="existing_category_Offer"),
    # path("add_product_offer", views.add_product_offer, name="add_product_offer"),
    # path("existing_product_Offer",views.existing_product_Offer,name="existing_product_Offer"),
    # path("add_banner", views.add_banner, name="add_banner"),
    # path("active_banners", views.active_banners, name="active_banners"),
    # path("editbanner/<banner_id>", views.editbanner, name="editbanner"),
    # path("deletebanner/<banner_id>", views.deletebanner, name="deletebanner"),
    # path("blockbanner/<banner_id>", views.blockbanner, name="blockbanner"),
    # path("unblockbanner/<banner_id>", views.unblockbanner, name="unblockbanner"),
    # path("blockBrandOffer/<brand_id>",views.blockBrandOffer,name="blockBrandOffer"),
    # path("unblockBrandOffer/<brand_id>",views.unblockBrandOffer,name="unblockBrandOffer"),
    # path("editBrandOffer/<brand_id>",views.editBrandOffer,name="editBrandOffer"),
    # path("deleteBrandOffer/<brand_id>",views.deleteBrandOffer,name="deleteBrandOffer"),
    # path("blockCategoryOffer/<category_id>",views.blockCategoryOffer,name="blockCategoryOffer"),
    # path("unblockCategoryOffer/<category_id>",views.unblockCategoryOffer,name="unblockCategoryOffer"),
    # path("editCategoryOffer/<category_id>",views.editCategoryOffer,name="editCategoryOffer"),
    # path("deleteCategoryOffer/<category_id>",views.deleteCategoryOffer,name="deleteCategoryOffer"),
    # path("blockProductOffer/<product_id>",views.blockProductOffer,name="blockProductOffer"),
    # path("unblockProductOffer/<product_id>",views.unblockProductOffer,name="unblockProductOffer"),
    # path("editProductOffer/<product_id>",views.editProductOffer,name="editProductOffer"),
    # path("deleteProductOffer/<product_id>",views.deleteProductOffer,name="deleteProductOffer"),
    
    
    
    
   
    
    