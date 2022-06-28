from math import prod
from os import times
from django.shortcuts import render

from django.shortcuts import render
from .decorators import *
from .utils import *
from .forms import *
from django.db.models import Count
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse, HttpResponseRedirect
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime

# Create your views here.
@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            customer = form.save()
            username = form.cleaned_data.get('username')
            Customer.objects.create(
                user=User.objects.get(username=username),
                name=form.cleaned_data.get('first_name'),
                phone=form.cleaned_data.get('phone')
            )
            return redirect('homepage')
    context = {'form': form}
    return render(request, 'store/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            print('username or password is incorrect')
    return render(request, 'store/login.html')

def logoutUser(request):
    logout(request)
    return redirect('homepage')

def homepage(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()[:10]
    categories = Category.objects.all()
    context = {
        'products': products, 'cartItems': cartItems, 'categories': categories,
    }
    return render(request, 'store/homepage.html', context)


def search(request):
    search_input = request.GET.get('global-search')

<<<<<<< HEAD
    products = Product.objects.filter(
        Q(title__icontains=search_input) | Q(subcategory__name__icontains=search_input))

    products_data = filterProducts(request, products)

    products = products_data['products']
    sizes = products_data['cycles']
    price_max = products_data['price_max']
    price_min = products_data['price_min']
    sort = products_data['sort_value']
    gender = products_data['gender']

    products = paginatorUtil(request, products)
    context = {'products': products, 'sizes': sizes, 'price_min': price_min,
               'price_max': price_max, 'sort_value': sort, 'gender': gender}
=======
    products = Product.objects.filter(title__icontains=search_input)

    products_data = filterProducts(request, products)

    # products = products_data['products']
    # sizes = products_data['cycles']
    # price_max = products_data['price_max']
    # price_min = products_data['price_min']
    # sort = products_data['sort_value']
    # gender = products_data['gender']

    products = paginatorUtil(request, products)
    context = {'products': products}
>>>>>>> 072c191317aa73da9ae42539e6a9a6c07e0c0602
    return render(request, 'store/search_result.html', context)


@login_required(login_url='login')
def userProfile(request):
    orders = request.user.customer.order_set.all()
    order_products = OrderProduct.objects.filter(
        order__in=orders)
    print(order_products)
<<<<<<< HEAD
=======
    print(orders)
>>>>>>> 072c191317aa73da9ae42539e6a9a6c07e0c0602

    context = {'orders': orders, 'order_products': order_products}
    return render(request, 'store/userProfile.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context=context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context=context)

def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category = category)

    products_data = filterProducts(request, products)
    products = products_data['products']
    sizes = products_data['sizes']
    price_max = products_data['price_max']
    price_min = products_data['price_min']
    sort = products_data['sort_value']
    gender = products_data['gender']
    # products = products.filter(
    #     reduce(lambda x, y: x | y, [Q(subcategory__name=item) for item in category]))
    products = paginatorUtil(request, products)

    context = {
<<<<<<< HEAD
               'category': category, 'products': products, 'sizes': sizes, 'price_min': price_min,
                'price_max': price_max, 'sort_value': sort,
                 'gender': gender}
=======
               'category': category, 'products': products, 'sizes': sizes, 'price_min': price_min, 'price_max': price_max, 'sort_value': sort, 'gender': gender}
>>>>>>> 072c191317aa73da9ae42539e6a9a6c07e0c0602
    return render(request, 'store/category.html', context)

def product(request, product_id):
    product = Product.objects.get(pk=product_id)
    context = {'product': product}
    return render(request, 'store/product.html', context)

def cancelOrder(request):
    data = json.loads(request.body)
    productId = data['productId']
    order = data['order']
    product = Product.objects.get(id=productId)
    customer = request.user.customer
    orderproduct = OrderProduct.objects.get(product=product, order=order)
    orderproduct.delete()
    return JsonResponse('Order Canceled', safe=False)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # cart_product_size = data['size']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderProduct, created = OrderProduct.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderProduct.quantity = (orderProduct.quantity + 1)
    elif action == 'remove':
        orderProduct.quantity = (orderProduct.quantity - 1)

    orderProduct.save()
    if orderProduct.quantity <= 0:
        orderProduct.delete()
    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    print(json.loads(request.body))
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    orderProducts = OrderProduct.objects.filter(order=order)
    if total == float(order.get_cart_total):
        order.complete = True
        for orderProduct in orderProducts:
            orderProduct.product.stockQuantity -= orderProduct.quantity
            orderProduct.product.save()
    order.save()

    # if order.complete:

    ShippingAdress.objects.get_or_create(
        customer=customer,
        order=order,
        city=data['shipping']['city'],
        street=data['shipping']['street'],
        house=data['shipping']['house'],
        appartament=data['shipping']['appartament']
    )
    return JsonResponse('Payment Complete', safe=False)







# ADMIN


@admin_only
def adminPanel(request):

    data = adminPanelProducts(request)
    orders = data['orders']
    unfinished_orders_count = data['unfinished_orders_count']
    new_unfinished_order = data['new_unfinished_order']
    earnings_overview = adminPanelEarningsOverview(request)
    order_products = data['order_products']
    print(new_unfinished_order)
    # shipping_adresses = data['shipping_adresses']
    months = earnings_overview['months']
    earnings_month_1 = earnings_overview['earnings_month_1']
    earnings_month_2 = earnings_overview['earnings_month_2']
    earnings_month_3 = earnings_overview['earnings_month_3']
    earnings_month_4 = earnings_overview['earnings_month_4']
    earnings_month_5 = earnings_overview['earnings_month_5']
    annual_earnings = earnings_overview['annual_earnings']

    total_customers = Customer.objects.aggregate(total=Count('user'))

    context = {'orders': orders,
<<<<<<< HEAD
               'order_products': order_products, 'months': months, 'earnings_month_1': earnings_month_1,
                'earnings_month_2': earnings_month_2, 'earnings_month_3': earnings_month_3,
                 'earnings_month_4': earnings_month_4, 'earnings_month_5': earnings_month_5,
                  'annual_earnings': annual_earnings, 
               'unfinished_orders_count': unfinished_orders_count, 'total_customers': total_customers,
                'new_unfinished_order':new_unfinished_order}
=======
               'order_products': order_products, 'months': months, 'earnings_month_1': earnings_month_1, 'earnings_month_2': earnings_month_2, 'earnings_month_3': earnings_month_3, 'earnings_month_4': earnings_month_4, 'earnings_month_5': earnings_month_5, 'annual_earnings': annual_earnings, 'unfinished_orders_count': unfinished_orders_count, 'total_customers': total_customers, 'new_unfinished_order':new_unfinished_order}
>>>>>>> 072c191317aa73da9ae42539e6a9a6c07e0c0602
    return render(request, 'store/adminPanel/adminPanel.html', context)


@admin_only
def showAllCategories(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    context = {'categories': categories, 'products':products}
    return render(request, 'store/adminPanel/all_categories.html', context)



@admin_only
def deleteCategory(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    if request.method == 'POST':
        category.delete()
        return redirect('all_categories')
    context = {'category': category, 'products':products}
    return render(request, 'store/adminPanel/delete_category.html', context)





@admin_only
def createProduct(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('create_product')
    context = {'form': form}
    return render(request, 'store/adminPanel/create_product.html', context)


@admin_only
def showCustomers(request):
    customers = Customer.objects.all()
    context = {'customers': customers}
    return render(request, 'store/adminPanel/customers.html', context)


@admin_only
def showCustomerOrders(request, customer_id):
    orders = Order.objects.filter(customer=customer_id, complete=True)
    order_products = OrderProduct.objects.filter(
        order__in=orders)
    customer = Customer.objects.get(id=customer_id)
    context = {'orders': orders,
               'order_products': order_products, 'customer': customer}
    return render(request, 'store/adminPanel/customer_orders.html', context)


@admin_only
def subCategoryforms(request):
    category_form = CategoryForm()
    
    context = {'category_form': category_form, }
    return render(request, 'store/adminPanel/add_category_subcategory.html', context)

@admin_only
def addCategory(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_category_subcategory')
    return redirect('admin_panel')


def is_valid_queryparam(param):
    return param != '' and param is not None
@admin_only
def products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    category_filter = request.GET.get('category_filter')
    product_title = request.GET.get('product_title')
    if is_valid_queryparam(product_title):
        products = products.filter(title__icontains=product_title)

    if is_valid_queryparam(category_filter):
        products = products.filter(category__name=category_filter)

    products = paginatorUtil(request, products)
    context = {'products': products, 'categories':categories, 'category_filter':category_filter}
    return render(request, 'store/adminPanel/products.html', context)


@admin_only
def updateProduct(request, pk):
    product = Product.objects.get(pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    context = {'form': form}
    return render(request, 'store/adminPanel/create_product.html', context)


@admin_only
def deleteProduct(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()

    return redirect('products_list')


@admin_only
def finishOrder(request, pk):
    order = Order.objects.get(pk=pk)
    order.finished = True
    order.save()
    return redirect('unfinished_orders')


@admin_only
def unfinishOrder(request, pk):
    order = Order.objects.get(pk=pk)
    order.finished = False
    order.save()
    return redirect('finished_orders')


@admin_only
def showOrder(request, pk):
    order = Order.objects.get(pk=pk)
    # orderproducts = OrderProduct.objects.filter(order=order)
    orderproducts = order.orderproduct_set.all()

    context = {'order': order, 'orderproducts': orderproducts}
    return render(request, 'store/adminPanel/order.html', context)


@admin_only
def finishedOrders(request):
    # data = adminPanelProducts(request)
    # orders = data['orders']
    # order_products = data['order_products']
    currentMonth = datetime.datetime.now().month
    orders = Order.objects.all()
    order_products = OrderProduct.objects.filter(
        order__in=orders)
    
    timeSort = request.GET.get('timeSort')
    exactDate = request.GET.get('exactDate')
    if is_valid_queryparam(exactDate):
        orders = Order.objects.filter(ordered_date__range = [exactDate, exactDate])
    if is_valid_queryparam(timeSort):
        if timeSort == 'thatMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth)
        if timeSort == 'previousMonth':
            orders=Order.objects.filter(ordered_date__month=currentMonth-1)
        if timeSort == 'lastMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=30))
        if timeSort == 'lastThreeMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=90))
  
    context = {'orders': orders,
               'order_products': order_products, }
    return render(request, 'store/adminPanel/finished_orders.html', context)


@admin_only
def unfinishedOrders(request):
    currentMonth = datetime.datetime.now().month
    data = adminPanelProducts(request)
    # unfinished_orders = data['unfinished_order']
    orders = Order.objects.filter(
        finished=False, complete=True)
    unfinished_orderProducts = OrderProduct.objects.filter(
        order__in=orders)
    timeSort = request.GET.get('timeSort')
    exactDate = request.GET.get('exactDate')
    if is_valid_queryparam(exactDate):
        orders = Order.objects.filter(ordered_date__range = [exactDate, exactDate], finished=False, complete=True)
    if is_valid_queryparam(timeSort):
        if timeSort == 'thatMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth, finished=False, complete=True)
        if timeSort == 'previousMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth-1, finished=False, complete=True)
        if timeSort == 'lastMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=30), finished=False, complete=True)
        if timeSort == 'lastThreeMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=90), finished=False, complete=True)
    context = {'unfinished_orders': orders,
               'unfinished_orderProducts': unfinished_orderProducts}
    return render(request, 'store/adminPanel/unfinished_orders.html', context)



@admin_only
def deleteOrder(request, pk):
    order = Order.objects.get(pk=pk)
    orderProducts = OrderProduct.objects.filter(order=order)
    for orderProduct in orderProducts:
        orderProduct.product.stockQuantity += orderProduct.quantity
        orderProduct.product.save()
    order.delete()
    return redirect('admin_panel')
