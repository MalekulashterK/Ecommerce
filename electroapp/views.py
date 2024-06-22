from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, logout, login
from electroapp.models import *
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils import timezone
import json
from django.db.models import F
from django.db.models.functions import TruncDate

def dashboard(request):

    if(request.user.is_authenticated == True):
        urole = request.user.role
        log = 'Yes'
    else:
        urole = 'NA'
        log = 'No'

    pdata = Product.objects.all()

    compact = {'urole':urole,'pdata':pdata, 'log':log}
    return render(request, 'dashboard.html',compact)

def dashboard1(request):
    
    return render(request, 'dashboard1.html')

def admin_panel(request):
    user_count = User.objects.count()
    product_count = Product.objects.count()
    order_count = 0


    compact = {'user_count':user_count,
               'product_count':product_count,
               'order_count':order_count}
    
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
    
    mydata = Product.objects.all()
    
    
    context = {'standards': mydata}
  
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

def place_order(request):
    now = datetime.now()
    user_id=User.objects.get(id=request.user.id).id
    auth_user=User.objects.get(id=user_id)

    k = json.loads(request.POST["cart_details"])

    total = 0

    for i in k:
        total = total + i['price']

    Order.objects.create(pdetail=k,
                         total=total,
                         created_by = auth_user,
                         created_at = now.strftime("%Y-%m-%d %H:%M:%S"),
                         updated_at = now.strftime("%Y-%m-%d %H:%M:%S"))
    
    messages.error(request, 'Data Submitted Successfully')
    return redirect('/')    
        

def my_order(request):

    distinct_dates = Order.objects.filter(created_by=request.user.id) \
    .annotate(date=TruncDate('created_at')) \
    .values('date') \
    .distinct()

    formatted_dates = [date['date'].strftime('%Y-%m-%d') for date in distinct_dates]

    data = []
    for fd in formatted_dates:

        datewise_order = Order.objects.filter(created_by=request.user.id, created_at__startswith = fd).all()

        total_product_no = 0
        total_product_amount = 0


        for dt in datewise_order:

            total_count = sum(item['count'] for item in dt.pdetail)
            total_amount = sum(item['price'] for item in dt.pdetail)


            total_product_no = total_product_no + total_count
            total_product_amount = total_product_amount + total_amount



        res = {}
        res['date'] = fd
        res['total_order_count'] = total_product_no
        res['total_product_amount'] = total_product_amount

        data.append(res)

    compact = {'data': data}
    return render(request,'order/my_orders.html',compact)


def my_order_details(request, id):

    date = id

    datewise_order = Order.objects.filter(created_at__startswith = date).values('pdetail')

    return HttpResponse(datewise_order)




