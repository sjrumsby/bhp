from django.conf.urls  import url, include
from rankings import views

urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^week/(?P<rankings_week>\d+)/', views.rankings_week, name="rankings_week"),
]
