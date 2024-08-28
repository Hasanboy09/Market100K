import re

from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Count, F
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView

from apps.forms import OrderForm, ProfileForm, StreamForm
from apps.models import Category, Product, User, Stream, Order


class HomeView(ListView):
    queryset = Category.objects.all()
    template_name = 'apps/product/home-page.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('search')  # noqa search tugmasi
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        data['popular_products'] = Product.objects.order_by('order_count')[:8]
        if q:
            data['products'] = Product.objects.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        data['popular_products'] = Product.objects.order_by('order_count')[:8]
        return data

    def get_queryset(self):
        query = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            return query.filter(name__icontains=search)
        return query


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        cat_slug = self.request.GET.get('category')
        query = super().get_queryset()
        if cat_slug:
            query = query.filter(category__slug=cat_slug)
        return query

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = Category.objects.all()
        return data


class ProductDetailView(DetailView, FormView):
    form_class = OrderForm
    model = Product
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        if form.is_valid():
            form = form.save(commit=False)
            form.user = self.request.user
            form.save()
        return render(self.request, 'apps/order/order.html', {'form': form})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        return data

    def form_invalid(self, form):
        print(10)


class CustomLoginView(TemplateView):
    template_name = 'apps/auth/login.html'

    def post(self, request, *args, **kwargs):  # noqa
        phone_number = re.sub(r'\D', '', request.POST.get('phone_number'))
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            # is_ = validators.validate_password(request.POST['PASSWORD'])

            user = User.objects.create_user(phone_number=phone_number, password=request.POST['password'])
            login(request, user)
            return redirect('profile')
        else:
            user = authenticate(request, username=user.phone_number, password=request.POST['password'])
            if user:
                login(request, user)
                next_url = request.GET.get('next')
                return redirect('profile')

            else:
                context = {
                    "messages_error": ["Invalid password"]
                }
                return render(request, template_name='apps/auth/login.html', context=context)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/dashboard.html'


class CallCenter(TemplateView):
    template_name = 'apps/dashboard/call-center.html'


class PaymentView(TemplateView):
    template_name = 'apps/profile/payment.html'


class ProfileFormView(FormView):
    form_class = ProfileForm
    template_name = 'apps/profile/profile.html'

    def form_valid(self, form):
        data = form.save(commit=False)
        print(data)

    def form_invalid(self, form):
        data = form.errors
        print(data)


class MarketListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/market/market-list.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('search')  # noqa  search tugmasi
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        if query:
            data['products'] = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return data

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            return queryset.filter(name__icontains=search)
        filter_value = self.request.GET.get('filter', 'new')
        if filter_value == 'popular':
            queryset = queryset.order_by('-order_count')
        elif filter_value == 'count':
            queryset = queryset.order_by('-count')
        elif filter_value == 'my-products':
            queryset = queryset.filter(owner=self.request.user)
        else:  # 'new'
            queryset = queryset.order_by('-created_at')
        return queryset


class StreamFormView(LoginRequiredMixin, FormView):
    form_class = StreamForm
    template_name = 'apps/market/market-list.html'

    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return redirect('stream-list')

    def form_invalid(self, form):
        print(form)


class StreamListView(ListView, View):
    queryset = Stream.objects.all()
    template_name = 'apps/market/stream/stream-list.html'
    context_object_name = 'streams'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        return data


class StreamDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        Stream.objects.filter(pk=pk).first().delete()
        return redirect('stream-list')


class StreamStatisticsListView(ListView):
    queryset = Stream.objects.all()
    template_name = 'apps/market/stream/stream-statistics.html'
    context_object_name = 'streams'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.get_queryset().aggregate(
            all_count=Sum('count'),
            all_new=Sum('new_count'),
            all_ready=Sum('ready_count'),
            all_deliver=Sum('deliver_count'),
            all_delivered=Sum('delivered_count'),
            all_cant_phone=Sum('cant_phone_count'),
            all_canceled=Sum('canceled_count'),
            all_archived=Sum('archived_count'),
        )
        context.update(query)
        return context

    def get_queryset(self):
        query = super().get_queryset().filter(owner=self.request.user).annotate(
            new_count=Count('orders', filter=Q(orders__status=Order.StatusType.NEW)),
            ready_count=Count('orders', filter=Q(orders__status=Order.StatusType.READY)),
            deliver_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVER)),
            delivered_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERED)),
            cant_phone_count=Count('orders', filter=Q(orders__status=Order.StatusType.CANT_PHONE)),
            canceled_count=Count('orders', filter=Q(orders__status=Order.StatusType.CANCELED)),
            archived_count=Count('orders', filter=Q(orders__status=Order.StatusType.ARCHIVED)),
        ).values('name', 'product__name', 'count', 'new_count',
                 'ready_count',
                 'deliver_count',
                 'delivered_count',
                 'cant_phone_count',
                 'canceled_count',
                 'archived_count')
        return query


class StreamOrderView(DetailView, FormView):
    form_class = OrderForm
    queryset = Stream.objects.all()
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'stream'

    def form_valid(self, form):
        if form.is_valid():
            form = form.save(commit=False)
            form.stream = self.get_object()
            form.user = self.request.user
            form.save()
        return render(self.request, 'apps/order/order.html', {'form': form})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object.product
        context['product'] = product
        stream_id = self.kwargs.get('pk')
        Stream.objects.filter(pk=stream_id).update(count=F('count') + 1)
        return context
