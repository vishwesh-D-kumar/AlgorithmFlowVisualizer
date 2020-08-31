from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run_tracer',views.run_tracer,name ='run_tracer'),
    path('step',views.show_step,name = 'step'),
    path('view_flowchart',views.view_flowchart,name='view_flowchart')
]