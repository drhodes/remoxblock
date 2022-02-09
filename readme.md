
# Work in progress!

remoxblock is an xblock that fetches serialized student answers from a
remote host and grades it against staff defined answers on the edx
platform.

![image](https://user-images.githubusercontent.com/84929/153287706-0522180d-121f-4056-87af-7f71a5c2f78d.png)


# Testing

1) activate a virtualenv

If you don't have a virtualenv, it's easy to set one up.

```bash 
$ virtualenv venv
$ source venv/bin/activate
```

Then install the xblock

$ pip install remoxblock 
$ make test

# Docs

For anyone who wants to hack on this project  
[Setting up development](https://github.com/drhodes/remoxblock/wiki/How-to-setup-for-development)  

For staff who wants to use remoxblock in a course (not ready yet)  
[Configuring remoxblock in Studio](https://github.com/drhodes/remoxblock/wiki/Staff-workflow-for-configuring-grader-from-Studio)  


[File server for grading Jupyterhub](https://github.com/drhodes/remoxblock/wiki/File-server-for-grading-Jupyterhub)


