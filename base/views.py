

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse

from activities.models import Activity, RoomActivity
from .models import (
    Room, Groups, Topic, Message

)
from .forms import (
    RoomForm, UserForm, MyUserCreationForm,
    GroupForm
)


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password= str(request.POST.get('password')).strip()

        user = User.objects.get(email=email)
        if user.check_password(password):
            login(request, user)
            return redirect('home')

        messages.error(request, f'No account matches this credentials')

    context = {'page': page}
    return render(request, 'base/auth/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        
        # avatar = request.FILES[0] if request.FILES[0] else None
        email = str(request.POST.get('email')).strip().lower()
        name = str(request.POST.get('name')).strip().capitalize()
        username = str(request.POST.get('username')).strip().lower()
        password_1 = str(request.POST.get('password')).strip()
        password_2 = str(request.POST.get('password_confirm')).strip()

        if not password_1 or not email or not username:
            messages.error(request, 'this field is required')
        elif password_1 != password_2:
            messages.error(request, 'password do not match')
        elif len(str(password_1)) < 8:
            messages.error(request, 'Password is too short')
        else:
            name = name.split() if name else ('', '')
            user = User.objects.create(
                email=email, username=username, 
                first_name=name[0], last_name=name[1], password=password_1
            )
            login(request, user)
            return redirect('home')


    return render(request, 'base/auth/register.html', {'form': form})


def home(request):
    logged_in_user = request.user
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    query = request.GET.get('query') if request.GET.get(
        'query') != None else ''

    topics = Topic.objects.all()
    topic_count = topics.count()

    userFollowTopics = []

    is_following = False
    room_count = 0
    for topic in topics:
        if logged_in_user in topic.followers.all():

            topic_rooms = topic.room_set.all()
            for room in topic_rooms:
                room_count += 1

            userFollowTopics.append(topic.room_set.all())
            is_following = True

    activity = Activity.objects.all().order_by('-date_issued')[:4]

    if q:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
        room_count = rooms.count()
        userFollowTopics = rooms

    if query:
        all_rooms = Room.objects.all()
        userFollowTopics = all_rooms
        room_count = all_rooms.count()

    if not request.user.is_authenticated:
        userFollowTopics = Room.objects.all()
        room_count = userFollowTopics.count()

    # return HttpResponse(f'{len(userFollowTopics)} topic lenth')
    context = {
        'q': q, 'query': query,
        'topics': topics[:5],
        'myrooms': userFollowTopics, 'room_count': room_count,
        'activities': activity, 'is_following': is_following,
        'topic_count':topic_count
    }
    return render(request, 'base/home/index.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        room_activity, new_room_activity = RoomActivity.objects.get_or_create(room=room)
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room/room_form.html', context)


def room(request, pk):
    room = Room.objects.get(pk=pk)
    groups = Groups.objects.filter(room=room)[:5]
    room_activity = RoomActivity.objects.filter(room=room).order_by('-date_issued')
    contributors = room.contributors.all()
 
    context = {
        'contributors': contributors,
        'groups': groups,
        'room': room,
        'room_activity': room_activity,
    }
    return render(request, 'base/room/room_view.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/room/group_msg__room_delete.html', {'obj': room})


@login_required(login_url='login')
def createGroup(request):
    form = GroupForm
    rooms = Room.objects.all()
    room_primary_key = request.GET.get('room_primary_key')
    # current_room = Room.objects.get(pk=room_primary_key)

    if request.method == 'POST':
        group_name = request.POST['group_room']

        try:
            room = Room.objects.get(name=group_name)
        except:
            room = None

        # Creating a new topic with a room
        if not room:
            topic_name = group_name + ' ' + 'Group'
            topic = Topic.objects.create(name=topic_name)
            room = Room.objects.create(
                name=group_name, host=request.user, topic=topic, contributors=request.user)
        else:
            room.contributors.add(request.user)

        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.room = room
            new_group.author = request.user
            new_group.save()
            
            room_activty, new_room_activty = RoomActivity.objects.get_or_create(room=room)
            if not new_group in room_activty.groups.all():
                room_activty.groups.add()

            return redirect('room', pk=room.pk)

    context = {
        'form': form,
        'rooms': rooms,
        # 'current_room': current_room,
    }
    return render(request, 'base/room/room_group_form.html', context)


def roomGroupChat(request, pk):
    group = Groups.objects.get(pk=pk)
    chats = Message.objects.filter(group=group)
    members = group.members.all()

    if request.method == 'POST':
        text = request.POST['body']
        message = Message.objects.create(
            body=text,
            user=request.user,
            group=group
        )
        group.members.add(request.user)

    context = {
        'group_messages': chats,
        'group_members': members,
        'group': group
    }
    return render(request, 'base/room/room_group_chat.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/user/profile.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/room/group_msg__room_delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/user/profile_update.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/miniview/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/miniview/activity.html', {'room_messages': room_messages})


def addTopicFollowers(request, pk):
    topic = Topic.objects.get(pk=pk)
    followers = topic.followers.all()

    is_following = False

    for follower in topic.followers.all():
        if request.user == follower:
            is_following = True

    if not is_following:
        topic.followers.add(request.user)
        return redirect(request.META['HTTP_REFERER'])
    else:
        topic.followers.remove(request.user)
        return redirect(request.META['HTTP_REFERER'])
