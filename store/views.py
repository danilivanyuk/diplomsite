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
    return render(request, 'store/search_result.html', context)


@login_required(login_url='login')
def userProfile(request):
    orders = request.user.customer.order_set.all()
    order_products = OrderProduct.objects.filter(
        order__in=orders)
    print(order_products)

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
               'category': category, 'products': products, 'sizes': sizes, 'price_min': price_min, 'price_max': price_max, 'sort_value': sort, 'gender': gender}
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
               'order_products': order_products, 'months': months, 'earnings_month_1': earnings_month_1, 'earnings_month_2': earnings_month_2, 'earnings_month_3': earnings_month_3, 'earnings_month_4': earnings_month_4, 'earnings_month_5': earnings_month_5, 'annual_earnings': annual_earnings, 'unfinished_orders_count': unfinished_orders_count, 'total_customers': total_customers, 'new_unfinished_order':new_unfinished_order}
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
    dateFrom = request.GET.get('dateFrom')
    dateTo = request.GET.get('dateTo')
    customerName = request.GET.get('customerName')
    productTitle = request.GET.get('productTitle')
    if is_valid_queryparam(exactDate):
        orders = Order.objects.filter(ordered_date__range = [exactDate, exactDate])
    elif is_valid_queryparam(timeSort):
        if timeSort == 'thatMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth)
        if timeSort == 'previousMonth':
            orders=Order.objects.filter(ordered_date__month=currentMonth-1)
        if timeSort == 'lastMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=30))
        if timeSort == 'lastThreeMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=90))
    elif is_valid_queryparam(dateFrom) and is_valid_queryparam(dateTo):
        orders = Order.objects.filter(ordered_date__range = [dateFrom, dateTo])
    elif is_valid_queryparam(dateFrom):
        orders=Order.objects.filter(ordered_date__gte=dateFrom)
        
    elif is_valid_queryparam(dateTo):
        orders=Order.objects.filter(ordered_date__lte=dateTo)
    elif is_valid_queryparam(customerName) and is_valid_queryparam(productTitle):
        orders = orders.filter(customer__name = customerName, orderproduct__product__title__icontains=productTitle)    
    elif is_valid_queryparam(customerName):
        orders = orders.filter(customer__name = customerName)
    elif is_valid_queryparam(productTitle):
        orders = orders.filter(orderproduct__product__title__icontains=productTitle)
        
  
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
    dateFrom = request.GET.get('dateFrom')
    dateTo = request.GET.get('dateTo')
    productTitle = request.GET.get('productTitle')
    customerName = request.GET.get('customerName')
    if is_valid_queryparam(exactDate):
        orders = Order.objects.filter(ordered_date__range = [exactDate, exactDate], finished=False, complete=True)
    elif is_valid_queryparam(timeSort):
        if timeSort == 'thatMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth, finished=False, complete=True)
        if timeSort == 'previousMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth-1, finished=False, complete=True)
        if timeSort == 'lastMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=30), finished=False, complete=True)
        if timeSort == 'lastThreeMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=90), finished=False, complete=True)
    elif is_valid_queryparam(dateFrom) and is_valid_queryparam(dateTo):
        orders = Order.objects.filter(ordered_date__range = [dateFrom, dateTo])
    elif is_valid_queryparam(dateFrom):
        orders=Order.objects.filter(ordered_date__gte=dateFrom)
        
    elif is_valid_queryparam(dateTo):
        orders=Order.objects.filter(ordered_date__lte=dateTo)
    elif is_valid_queryparam(customerName) and is_valid_queryparam(productTitle):
        orders = orders.filter(customer__name = customerName, orderproduct__product__title__icontains=productTitle)
    elif is_valid_queryparam(customerName):
        orders = orders.filter(customer__name = customerName)
    elif is_valid_queryparam(productTitle):
        orders = orders.filter(orderproduct__product__title__icontains=productTitle)
    
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

import xlwt
@admin_only
def productReports(request):
    
    categories = Category.objects.all()
    category_filter = request.GET.get('category_filter')
    product_title = request.GET.get('product_title')
    a = []
    print(a)
    if is_valid_queryparam(product_title):
        products = Product.objects.filter(title__icontains=product_title)
        for i in products:
            print(i)
            a.append(i.id)

    elif is_valid_queryparam(category_filter):
        products = Product.objects.filter(category__name=category_filter)
        for i in products:
            a.append(i.id)
    else:
        products = Product.objects.all()
        for i in products:
            print(i)
            a.append(i.id)

    if request.method == 'POST':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Products.xls"'

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Товары')
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        font_style.font.height = 320
        font_style.alignment.horz = xlwt.Alignment.HORZ_CENTER

        ws.write_merge(1, 3, 3,8, "Список Товаров", font_style)
        row_num = 5
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        font_style.font.height= 280
        font_style.borders.top = 2
        font_style.borders.right = 2
        font_style.borders.left = 2
        font_style.borders.bottom = 2

        columns = ['Название', 'Категория', 'Серийный н.', 'Циклы','Цвет', 'Количество', 'Цена покупки', 'Цена продажи']
        ws.col(2).width = 7000 # Название
        ws.col(3).width = 10000 #Категория
        ws.col(4).width = 5000 #Серийный номер
        ws.col(5).width = 3500 #Циклы
        ws.col(6).width = 4000 #Цвет
        ws.col(7).width = 4500 # Количество
        ws.col(8).width = 5000 # Цена покупки
        ws.col(9).width = 5200 # Цена продажи
        # ws.col(10).width = 3000 # счет

        for col_num in range(len(columns)):
            ws.write(row_num, col_num+2, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        font_style.font.height = 240
        font_style.borders.top = 1
        font_style.borders.right = 1
        font_style.borders.left = 1
        font_style.borders.bottom = 1

        rows = Product.objects.filter(id__in = a).values_list('title', 'category__name', 'serialNumber', 'cycles','color', 'stockQuantity', 'priceBuy', 'priceSell')

        for row in rows:
            print(row)
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num+2, row[col_num], font_style)
        wb.save(response)
        return response

    context = {'products': products, 'categories':categories, 'category_filter':category_filter}
    return render(request, 'store/adminPanel/product_reports.html', context)


@admin_only
def orderReports(request):
    currentMonth = datetime.datetime.now().month
    
    a = []
    timeSort = request.GET.get('timeSort')
    exactDate = request.GET.get('exactDate')
    dateFrom = request.GET.get('dateFrom')
    dateTo = request.GET.get('dateTo')
    productTitle = request.GET.get('productTitle')
    customerName = request.GET.get('customerName')
    if is_valid_queryparam(exactDate):
        orders = Order.objects.filter(ordered_date__range = [exactDate, exactDate])
        for i in orders:
            a.append(i.id)
    elif is_valid_queryparam(timeSort):
        if timeSort == 'thatMonth':
            orders=Order.objects.filter(ordered_date__month__gte=currentMonth)
            for i in orders:
                a.append(i.id)
        if timeSort == 'previousMonth':
            orders=Order.objects.filter(ordered_date__month=currentMonth-1)
            for i in orders:
                a.append(i.id)
        if timeSort == 'lastMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=30))
            for i in orders:
                a.append(i.id)
        if timeSort == 'lastThreeMonth':
            orders = Order.objects.filter(ordered_date__gte=datetime.datetime.now()-timedelta(days=90))
            for i in orders:
                a.append(i.id)
    elif is_valid_queryparam(dateFrom) and is_valid_queryparam(dateTo):
        print(dateFrom, dateTo)
        orders = Order.objects.filter(ordered_date__range = [dateFrom, dateTo])
        for i in orders:
            a.append(i.id)
    elif is_valid_queryparam(dateFrom):
        orders=Order.objects.filter(ordered_date__gte=dateFrom)
        for i in orders:
            a.append(i.id)
    elif is_valid_queryparam(dateTo):
        orders=Order.objects.filter(ordered_date__lte=dateTo)
        for i in orders:
            a.append(i.id)
    elif is_valid_queryparam(customerName) and is_valid_queryparam(productTitle):
        orders = Order.objects.filter(customer__name = customerName, orderproduct__product__title__icontains=productTitle)
        for i in orders:
            a.append(i.id)
    elif is_valid_queryparam(customerName):
        orders = Order.objects.filter(customer__name = customerName)
        for i in orders:
            a.append(i.id)
    elif is_valid_queryparam(productTitle):
        orders=Order.objects.filter(orderproduct__product__title__icontains=productTitle)
        for i in orders:
            a.append(i.id)
    else:
        orders = Order.objects.all()
        for i in orders:
            a.append(i.id)

    
    order_products = OrderProduct.objects.filter(
        order__in=orders)


    print(a)
    if request.method == 'POST':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Products.xls"'

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Товары', cell_overwrite_ok=True)
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        font_style.font.height = 320
        font_style.alignment.horz = xlwt.Alignment.HORZ_CENTER

        ws.write_merge(1, 3, 3, 7, "Список Заказов", font_style)
        row_num = 5
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        font_style.font.height= 280
        font_style.borders.top = 2
        font_style.borders.right = 2
        font_style.borders.left = 2
        font_style.borders.bottom = 2

        columns = ['Имя', 'Телефон', 'Дата заказа', 'Город','Улица', 'Дом', 'Квартира']
        ws.col(2).width = 7000 # Имя
        ws.col(3).width = 10000 #Телефон
        ws.col(4).width = 5000 #Дата заказа
        ws.col(5).width = 3500 #Город
        ws.col(6).width = 4000 #Улица
        ws.col(7).width = 4500 # Дом
        ws.col(8).width = 5000 # Квартира
        # ws.col(9).width = 5200 # Цена продажи
        # ws.col(10).width = 3000 # счет

        for col_num in range(len(columns)):
            ws.write(row_num, col_num+2, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        font_style.font.height = 240
        font_style.borders.top = 1
        font_style.borders.right = 1
        font_style.borders.left = 1
        font_style.borders.bottom = 1

        rows = Order.objects.filter(id__in = a, complete = True)
        # rows = Product.objects.filter(id__in = a).values_list('title', 'category__name', 'serialNumber', 'cycles','color', 'stockQuantity', 'priceBuy', 'priceSell')

        for row in rows:
            order_details = Order.objects.filter(id = row.id, complete=True).values_list('customer__name', 'customer__phone','ordered_date', 'shippingadress__city', 'shippingadress__street', 'shippingadress__house', 'shippingadress__appartament')
            order_products_details = OrderProduct.objects.filter(order = row.id, order__complete=True).values_list('product__title', 'product__serialNumber', 'product__color', 'quantity', 'product__priceSell')
            
            row_num += 1
            orderDate = ''
            getDate = Order.objects.filter(id = row.id).values_list('ordered_date')
            for i in getDate:
                for x in i:
                    orderDate = str(x)

            orderTotal = Order.objects.get(id=row.id).get_cart_total
            print(orderTotal)
            

            order_row_num = row_num+1
            for i in order_details:
                for col_num in range(7):
                    ws.write(row_num, col_num+2, i[col_num], font_style)
            ws.write(row_num, 4, orderDate, font_style)
            for order_product in order_products_details:
                for col_num in range(5):
                    ws.write(order_row_num, col_num+2, order_product[col_num], font_style)
                order_row_num += 1
            ws.write(order_row_num-1, 7, 'Итого: ', font_style)
            ws.write(order_row_num-1, 8, orderTotal, font_style)
            
                    
            row_num = order_row_num+1
            

                # ws.write(row_num, col_num+2, 'priv)', font_style)
        wb.save(response)
                
            
        return response
  
    context = {'orders': orders,
               'order_products': order_products, }
    return render(request, 'store/adminPanel/order_reports.html', context)