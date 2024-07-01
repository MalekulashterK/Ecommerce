from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, logout, login, get_user_model
from electroapp.models import *
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils import timezone
from .forms import CustomUserCreationForm

import json
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import F
from django.db.models.functions import TruncDate
import pandas as pd

User = get_user_model()

def dashboard(request):
    
    if(request.user.is_authenticated == True):
        urole = request.user.role
        log = 'Yes'
    else:
        urole = 'NA'
        log = 'No'

    pdata = Product.objects.all()
    category = Category.objects.all()

    compact = {'urole':urole,'pdata':pdata,'log':log, 'category':category}
    return render(request, 'dashboard.html',compact)

def search_category(request, id):

    if(request.user.is_authenticated == True):
        urole = request.user.role
        log = 'Yes'
    else:
        urole = 'NA'
        log = 'No'

    pdata = Product.objects.filter(category = id).all()
    category = Category.objects.all()

    compact = {'urole':urole,'pdata':pdata,'log':log, 'category':category, 'id':id}
    return render(request, 'search_category.html',compact)


def dashboard1(request):
    
    return render(request, 'dashboard1.html')

@login_required(login_url="/user_login")
def after_order(request):
    
    last_order = Order.objects.filter(created_by=request.user.id).order_by('-created_at').values()[0]

    return render(request, 'after_order.html',{'last_order':last_order})


def admin_panel(request):
    user_count = User.objects.count()
    product_count = Product.objects.count()
    order_count = Category.objects.count()



    distinct_dates = Order.objects.annotate(date=TruncDate('created_at')) \
    .values('date') \
    .distinct()

    formatted_dates = [date['date'].strftime('%Y-%m-%d') for date in distinct_dates]

    sorted_dates = sorted(datetime.strptime(date, "%Y-%m-%d") for date in formatted_dates)

    formatted_dates = [date.strftime("%Y-%m-%d") for date in sorted_dates]


    data = []
    for fd in formatted_dates:

        datewise_order = Order.objects.filter(created_at__startswith = fd).all()

        total_product_no = 0
        total_product_amount = 0


        for dt in datewise_order:

            total_count = sum(item['count'] for item in dt.pdetail)
            total_amount = sum(item['price'] * item['count'] for item in dt.pdetail)


            total_product_no = total_product_no + total_count
            total_product_amount = total_product_amount + total_amount



        res = {}
        res['date'] = fd
        res['total_order_count'] = total_product_no
        res['total_product_amount'] = total_product_amount

        data.append(res)

    dates = [entry['date'] for entry in data]
    order_counts = [entry['total_order_count'] for entry in data]
    fig, ax = plt.subplots()
    ax.bar(dates, order_counts, color='green', alpha=0.6)
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Order Count')
    ax.set_title('Date vs Total Order Count')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()


    dates = [entry['date'] for entry in data]
    order_amount = [entry['total_product_amount'] for entry in data]
    fig, ax1 = plt.subplots()
    ax1.plot(dates, order_amount, color='blue', alpha=0.6, marker='o')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Total Order Amount')
    ax1.set_title('Date vs Total Order Amount')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64_1 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()


    compact = {'user_count':user_count,
               'product_count':product_count,
               'order_count':order_count,
               'chart': image_base64,
               'chart1':image_base64_1}
    
    return render(request, 'admin_panel.html', compact)



def user_register(request):
    now = datetime.now()
    if request.method == 'POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        password=request.POST['password']
        role='User'
        u = User.objects.create(username=email, email=email, first_name=first_name,last_name=last_name,role=role)
        u.set_password(password)
        u.save()
        
  
        return redirect('/user_login/')
    return render(request, '/user_login')


def user_login(request):
    if request.method == 'POST':
        if User.objects.filter(username = request.POST['username']).exists():
            user = authenticate(request, username = request.POST['username'], password = request.POST['password'])

            if user is None:
                messages.error(request, 'Wrong Password Given')
                return redirect('/user_login')
            else:
                login(request, user)
                return redirect('/dashboard/')
        messages.error(request, 'Wrong Password Given')
        return redirect('/')
    return render(request, 'login/login.html')


@login_required(login_url = "/user_login/")
def user_logout(request):
    logout(request)
    return redirect('/dashboard/')



# Standard Master
@login_required(login_url = "/user_login")
def productindex(request):
    now = datetime.now()
    auth_user=User.objects.get(id=request.user.id)

    
    if request.method == 'POST':
        pdtcount = Product.objects.filter(pname=request.POST['pname']).count()
        
        if pdtcount > 0:
            messages.warning(request, 'Product with this standard already exists.')
        else:
            # Get current authenticated user
            auth_user = request.user
            
            # Get current timestamp
            now = timezone.now()
            
            # Handle file upload
            image_file = request.FILES['image']
            

            
            # Create Product object
            Product.objects.create(
                pname=request.POST['pname'],
                category=request.POST['category'],
                description=request.POST['description'],
                price=request.POST['price'],
                qty=request.POST['qty'],
                image=image_file,  # Save the path to the uploaded file
                created_at=now,
                updated_at=now,
                created_by=auth_user,
                updated_by=auth_user
            )
            
            messages.success(request, 'Data Submitted Successfully')
            return redirect('/productindex/')
    
    mydata = Product.objects.order_by('-created_at').all()
    category = Category.objects.all()

    
    
    context = {'standards': mydata, 'category':category}
  
    return render(request,'product/index.html',context)

@login_required(login_url = "/user_login")
def product_update(request, id):
    now = datetime.now()
    auth_user=User.objects.get(id=request.user.id)

    product_data = Product.objects.get(id=id)
    
    if product_data.standard == request.POST['standard']:
    
        Product.objects.filter(id=id).update(standard = request.POST['standard'],
                 updated_by = auth_user,
                updated_at = now.strftime("%Y-%m-%d %H:%M:%S"))
        
        messages.info(request, 'Data Submitted Successfully')
        return redirect('/standardindex/')
        
    else:
        standcount = Product.objects.filter(standard=request.POST['standard']).count()
         
        if standcount > 0:
            messages.warning(request, 'Data Submitted Successfully')
        else:
            Product.objects.filter(id=id).update(standard = request.POST['standard'],
            updated_by = auth_user,
            updated_at = now.strftime("%Y-%m-%d %H:%M:%S"))
        
            messages.info(request, 'Data Submitted Successfully')
            return redirect('/standardindex/')

@login_required(login_url = "/user_login")
def product_delete(request, id):
    Product.objects.filter(id=id).delete()
    messages.error(request, 'Data Submitted Successfully')
    return redirect('/standardindex/')     

@login_required(login_url = "/user_login")
def place_order(request):
    now = datetime.now()
    user_id=User.objects.get(id=request.user.id).id
    auth_user=User.objects.get(id=user_id)

    count = Order.objects.count()

    order_id = 'ODR'+'-'+'000'+str(count + 1)
    

    k = json.loads(request.POST["cart_details"])

    total = 0

    for i in k:
        total = total + i['price']
    if len(k) > 0:
        Order.objects.create(pdetail=k,
                            order_id = order_id,
                            total=total,
                            created_by = auth_user,
                            created_at = now.strftime("%Y-%m-%d %H:%M:%S"),
                            updated_at = now.strftime("%Y-%m-%d %H:%M:%S"))
        
    messages.error(request, 'Data Submitted Successfully')
    return redirect('/after_order')    
        
@login_required(login_url = "/user_login")
def my_order(request):

    distinct_dates = Order.objects.filter(created_by=request.user.id) \
    .annotate(date=TruncDate('created_at')) \
    .values('date') \
    .distinct()

    formatted_dates = [date['date'].strftime('%Y-%m-%d') for date in distinct_dates]

    data = []
    for fd in formatted_dates[::-1]:

        datewise_order = Order.objects.filter(created_by=request.user.id, created_at__startswith = fd).all()

        total_product_no = 0
        total_product_amount = 0


        for dt in datewise_order:

            total_count = sum(item['count'] for item in dt.pdetail)
            total_amount = sum(item['price'] * item['count'] for item in dt.pdetail)


            total_product_no = total_product_no + total_count
            total_product_amount = total_product_amount + total_amount



        res = {}
        res['date'] = fd
        res['total_order_count'] = total_product_no
        res['total_product_amount'] = total_product_amount

        data.append(res)

    compact = {'data': data}
    return render(request,'order/my_orders.html',compact)

@login_required(login_url = "/user_login")
def my_order_details(request, id):

    date = id

    datewise_order = Order.objects.filter(created_at__startswith = date).values('pdetail')

    # return HttpResponse(datewise_order)
    order_details = []
    total_qty = 0
    total_price = 0

    for do in datewise_order:



        for dat in do['pdetail']:

            val = Order.objects.filter(pdetail = do['pdetail']).get()
            orders = {}
            orders['order_id'] = val.order_id
            orders['name'] = dat['name']
            orders['price'] = dat['price']
            orders['qty'] = dat['count']

            total_qty =  total_qty + dat['count']
            total_price = total_price + dat['price']

            order_details.append(orders)


    compact = {'date':date,'order_details':order_details,'total_qty':total_qty,'total_price':total_price}
    
    return render(request,'order/my_order_details.html', compact)
  

@login_required(login_url = "/user_login")
def categoryindex(request):
    now = datetime.now()
    auth_user=User.objects.get(id=request.user.id)

    
    if request.method == 'POST':
        catcount = Category.objects.filter(category_name=request.POST['category_name']).count()
        
        if catcount > 0:
            messages.warning(request, 'Category already exists.')
        else:
            # Get current authenticated user
            auth_user = request.user
            
            # Get current timestamp
            now = timezone.now()
         

            
            # Create Product object
            Category.objects.create(
                category_name=request.POST['category_name'],
                created_at=now,
                updated_at=now,
                created_by=auth_user,
                updated_by=auth_user
            )
            
            messages.success(request, 'Data Submitted Successfully')
            return redirect('/categoryindex/')
    
    mydata = Category.objects.order_by('-created_at').all()
    
    
    context = {'standards': mydata}
  
    return render(request,'category/index.html',context)


@login_required(login_url = "/user_login")
def category_update(request, id):
    now = datetime.now()
    auth_user=User.objects.get(id=request.user.id)

    category_data = Category.objects.get(id=id)
    
   
    Category.objects.filter(id=id).update(category_name = request.POST['category_name'],
                updated_by = auth_user,
            updated_at = now.strftime("%Y-%m-%d %H:%M:%S"))
    
    messages.info(request, 'Data Submitted Successfully')
    return redirect('/categoryindex/')


@login_required(login_url = "/user_login")
def category_delete(request, id):
    Category.objects.filter(id=id).delete()
    messages.error(request, 'Data Submitted Successfully')
    return redirect('/categoryindex/')     


def users(request):

    user = User.objects.all()
    context = {'user':user}

    return render(request,'users.html',context)


def order_report(request):

    now = datetime.now()

    if request.method == 'POST':

        from_date_str = request.POST['from_date']
        to_date_str = request.POST['to_date']

    else:

        from_date_str = now.strftime("%Y-%m-%d")
        to_date_str = now.strftime("%Y-%m-%d")

    from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

    date_range = pd.date_range(start=from_date, end=to_date).strftime("%Y-%m-%d").tolist()


    data = []
    for fd in date_range[::-1]:

        datewise_order = Order.objects.filter(created_at__startswith = fd).all()

        total_product_no = 0
        total_product_amount = 0


        for dt in datewise_order:

            total_count = sum(item['count'] for item in dt.pdetail)
            total_amount = sum(item['price'] * item['count'] for item in dt.pdetail)


            total_product_no = total_product_no + total_count
            total_product_amount = total_product_amount + total_amount



        res = {}
        res['date'] = fd
        res['total_order_count'] = total_product_no
        res['total_product_amount'] = total_product_amount

        if total_product_no > 0:

            data.append(res)    

    compact = {'data':data, 'from_date':from_date_str,  'to_date':to_date_str}
    return render(request,'order/order_report.html', compact)


def order_report_in(request, id):
    date = id

    datewise_order = Order.objects.filter(created_at__startswith = date).all()


    data = []
    total_count = 0
    total_amount = 0

    for do in datewise_order:

        auth_user=User.objects.get(id = do.created_by_id)

        total_count = sum(item['count'] for item in do.pdetail)
        total_amount = sum(item['price'] * item['count'] for item in do.pdetail)

        res = {}
        res['order_id'] = do.order_id
        res['count'] = total_count
        res['amount'] = total_amount
        res['created_by'] = auth_user.first_name+' '+auth_user.last_name
        res['order_data'] = do.pdetail
        data.append(res)

    compact = {'date':date, 'data':data}
    return render(request,'order/order_report_in.html',compact)
