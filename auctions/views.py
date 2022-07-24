from unicodedata import name
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .models import Listing, Category, Watchlist, Bid, Comment
from .forms import ListingForm

from .models import User


def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            author = request.user
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]
            image = form.cleaned_data["image"]

            # Attempt to create new listing
            print('category', category)
            print('user', author)
            try:
                listing = Listing.objects.create(author=author, title=title, description=description, price=price, bid=None, 
                    category=category, image=image, is_active=True)
                listing.save()
            except IntegrityError:
                return render(request, "auctions/create_listing.html", {
                    "message": "Catched error."
                })

            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        else:
            return render(request, 'auctions/create_listing.html', {
                'form': ListingForm(),
                'message': 'Form not valid'
            })
    
    else:
        return render(request, 'auctions/create_listing.html', {
            'form': ListingForm()
        })

@login_required(login_url='login')
def category(request, category):
    category = Category.objects.get(name=category)
    listings = Listing.objects.filter(category=category)
    return render(request, 'auctions/category.html',{
        'listings': listings,
        'category': category
    })

@login_required(login_url='login')
def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })

@login_required(login_url='login')
def listing(request, listing_id):
    # user
    user = request.user

    # Listing Cache
    if cache.get(listing_id):
        listing = cache.get(listing_id)
    else:
        listing = Listing.objects.get(pk=listing_id)
        cache.set(listing_id, listing)

    # Watchlist
    try:
        watchlist = Watchlist.objects.get(user=user)
    except Watchlist.DoesNotExist:
        watchlist = None

    if watchlist != None and listing in watchlist.listings.all():
        in_watchlist = True
    else:
        in_watchlist = False
    
    
    # Bid
    bid = Bid.objects.filter(listing_id=listing_id)
    n_bids = bid.count()

    is_current_bid = False
    if n_bids > 0:
        is_current_bid = bid.get(is_current=True).user == user
    
    # Comments
    comments = Comment.objects.filter(listing_id=listing_id)

    
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'in_watchlist': in_watchlist,
        'n_bids': n_bids,
        'is_current_bid': is_current_bid,
        'comments': comments
    })

@login_required(login_url='login')
def watchlist(request, listing_id=None):
    if request.method == "POST":
        user = request.user
        # Listing Cache
        if cache.get(listing_id):
            listing = cache.get(listing_id)
        else:
            listing = Listing.objects.get(pk=listing_id)
            cache.set(listing_id, listing)

        is_add = request.POST["add"]

        try:
            watchlist = Watchlist.objects.get(user=user)
        except:
            Watchlist.objects.create(user=user)
            watchlist = Watchlist.objects.get(user=user)
        
        if is_add == 'yes':
            watchlist.listings.add(listing)
        else:
            watchlist.listings.remove(listing)
        return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
    else:
        user = request.user
        try:
            watchlist = Watchlist.objects.get(user=user)
            listings = watchlist.listings.all()
        except Watchlist.DoesNotExist:
            listings = None

        return render(request, 'auctions/watchlist.html', {
            'listings': listings
        })

@login_required(login_url='login')
def bid(request, listing_id):
    if request.method == "POST":
        user = request.user
        # Listing Cache
        if cache.get(listing_id):
            listing = cache.get(listing_id)
        else:
            listing = Listing.objects.get(pk=listing_id)
            cache.set(listing_id, listing)
        print(listing.price)
        bid_value = request.POST["bid"]

        if bid_value == '':
            bid_value = 0.0
        else:
            bid_value = float(bid_value)
        
        if listing.is_active:
            # if the bid is higher than current price
            if bid_value > listing.price:
                # if the bidder is not the author
                if listing.author != user:
                    listing_bids = Bid.objects.filter(listing_id=listing_id)
                    
                    if listing_bids.count() > 0:
                        current_bid = listing_bids.get(is_current=True)
                        current_bid.is_current = False
                        current_bid.save()
    
                    bid = Bid(user=user, listing=listing, value=bid_value, is_current=True)
                    bid.save()

                    listing.price = bid_value
                    listing.save()
                    cache.set(listing_id, listing)

                    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
                    #
                else:
                    messages.error(request, 'You can\'t bid, your are the author.')
                    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
            else:
                messages.error(request, 'Your bid is lower than the current bid.')
                return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
        else:
            messages.error(request, 'Auction closed.')
            return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))

@login_required(login_url='login')
def close_listing(request, listing_id):
    if request.method == "POST":
        user = request.user
        if cache.get(listing_id):
            listing = cache.get(listing_id)
        else:
            listing = Listing.objects.get(pk=listing_id)

        if user == listing.author:
            listing.is_active = False
            listing.save()
            cache.set(listing_id, listing)

    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))

@login_required(login_url='login')
def comment(request, listing_id):
    if request.method == "POST":
        user = request.user
        if cache.get(listing_id):
            listing = cache.get(listing_id)
        else:
            listing = Listing.objects.get(pk=listing_id)

        content = request.POST["content"]
        if content != '':
            comment = Comment(user=user, listing=listing, content=content)
            comment.save()

    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))