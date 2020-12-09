from django.shortcuts import render
from django.contrib import messages
import markdown2
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
import secrets

from . import util

# Class for form used in search page
class newEntryForm(forms.Form):
    title = forms.CharField(label='Entry title', widget=forms.TextInput(attrs={'placeholder': 'Entry title', 'class' : 'form-control col-md-2'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows' : 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, name):
    
    # Check if entry exists            
    if util.get_entry(name) is None:
        messages.error(request, 'was not found')
        return render(request, "encyclopedia/entry.html", {
            "title" : name.capitalize()
        })
    else:
        # return page displaying entry information
        return render(request, "encyclopedia/entry.html", {
            "name" : markdown2.markdown(util.get_entry(name)),
            "title" : name,
        })

def search(request):

    # check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = request.POST.get('q')

        try:
            # Search the entry in encyclopedia
            newEntry = markdown2.markdown(util.get_entry(form))

            # Return page displaying entry info
            return render(request, "encyclopedia/entry.html",{
                    "name" : newEntry
            })
        except:
            # create empty list
            entry_list = []

            # Loop through list of entries for a substring of user input.
            entries = util.list_entries()
            
            for entry in entries:
                # add entry to our list in lowercase format
                entry_list.append(entry.lower())
            
            # check for substring in list of entries and create new list
            entry_with_substring = [i for i in entry_list if request.POST.get('q').lower() in i]

            # check if entry_list is not empty
            if entry_with_substring != []:
                
                # change to captilize
                for x in range(len(entry_with_substring)):
                    entry_with_substring[x] = entry_with_substring[x].capitalize()
                
                # render page with list of entries with substring
                return render(request, "encyclopedia/search.html",{
                    "entrylist" : entry_with_substring
                })
            else:
                messages.error(request, 'was not found')
                return render(request, "encyclopedia/entry.html", {
                    "title" : form.capitalize()
                })
      
    else:
        # render layout page
        return render(request, "encyclopedia/layout.html")

def newEntry(request):

    # check if method is post
    if request.method == "POST":

        # save input as form
        form = newEntryForm(request.POST)

        # check if form is valid
        if form.is_valid():
            # Isolate the values from the cleaned version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # check if entry exists or its an edit
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", args=[title]))
            else:
                # return that form with error message
                return render(request, "encyclopedia/newEntry.html", {
                    "form" : form,
                    "existing" : True,
                    "entry" : title
                })
    else:
        # incase its a get or another method
        return render(request, "encyclopedia/newEntry.html", {
            "form" : newEntryForm(),
            "existing" : False
        })

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        messages.error(request, 'was not found')
        return render(request, "encyclopedia/entry.html", {
            "title" : entry.capitalize()
        })
    else:
        # Display existing entry data for user to edit
        form = newEntryForm()
        form.fields["title"].initial = entry     
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newEntry.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entryTitle": form.fields["title"].initial
        })  

def random(request):
    # Display random page for user once link is clicked 
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'name': randomEntry}))      

