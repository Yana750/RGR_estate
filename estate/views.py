from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.urls import reverse_lazy

from .models import Rent, Category
from .forms import RentCreateForm, RentUpdateForm
# Create your views here.

#наследуемся от ListView класс, это представление будет обрабатывать список объектов
class RentListView(ListView):
    #название нашей модели
    model = Rent
    #название шаблона вывода объектов
    template_name = 'rent/rent_list.html'
    #переменная, в которой будет хранится список для вывода в шаблоне
    context_object_name = 'rents'
    paginate_by = 2

    queryset = Rent.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context
    
class RentDetailView(DetailView):
    #название нашей модели
    model = Rent
    #название шаблона вывода объектов
    template_name = 'rent/rent_detail.html'
    #переменная, в которой будет хранится список для вывода в шаблоне
    context_object_name = 'rents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context

class RentByCategoryListView(ListView):
    #название нашей модели
    model = Rent
    #название шаблона вывода объектов
    template_name = 'rent/rent_list.html'
    #переменная, в которой будет хранится список для вывода в шаблоне
    context_object_name = 'rents'
    category = None

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Rent.objects.all().filter(category__slug=self.category.slug)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Объявления из категории: {self.category.title}' 
        return context

def rent_list(request):
    rents = Rent.objects.all()
    paginator = Paginator(rents, per_page=2)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    context = {'page_obj': page_object}
    return render(request, 'rent/rent_func_list.html', context)

class RentCreateView(CreateView):
    """
    Представление: создание материалов на сайте
    """
    model = Rent
    template_name = 'rent/rents_create.html'
    form_class = RentCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление объявления на сайт'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)
    
class RentUpdateView(UpdateView):
    """
    Представление: обновления материала на сайте
    """
    model = Rent
    template_name = 'rent/rents_update.html'
    context_object_name = 'rent'
    form_class = RentUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление объявления: {self.object.title}'
        return context
    
    def form_valid(self, form):
        # form.instance.updater = self.request.user
        form.save()
        return super().form_valid(form)
    
class RentDeleteView(DeleteView):
    """
    Представление: удаления материала
    """
    model = Rent
    success_url = reverse_lazy('home')
    context_object_name = 'rent'
    template_name = 'rent/rents_delete.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление объявления: {self.object.title}'
        return context