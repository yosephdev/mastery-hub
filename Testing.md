# Testing

Return back to the [README.md](README.md) file.

During the development of this project, I conducted various tests to ensure the proper functioning of the website. In this section, you will find documentation on all tests performed on the site.

## Code Validation

I tested all my code using each language's preferred programming tools.

### HTML

I have used the recommended [HTML W3C Validator](https://validator.w3.org) to validate all of my HTML files.

| Page             | W3C URL                                                                                                                                                       | Screenshot                                     | Notes               |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|---------------------|
| Home             | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2F)                                                             | ![screenshot](docs/readme_images/image-54.png) | Pass: No Errors     |
| Sessions Page    | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Fmasteryhub%2Fsessions%2F)                                     | ![screenshot](docs/readme_images/image-55.png) | Pass: No Errors     |
| Session Detail   | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F%3Fnext%3D%2Fmasteryhub%2Fsessions%2F2%2F) | ![screenshot](docs/readme_images/image-56.png) | Pass: No Errors     |
| Contact          | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Fcontact%2F)                                                         | ![screenshot](docs/readme_images/image-57.png) | Pass: No Errors     |
| Sign Up          | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F)                                            | ![screenshot](docs/readme_images/image-58.png) | Fail: Errors found  |
| Sign In          | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F)                                             | ![screenshot](docs/readme_images/image-59.png) | Pass: No Errors     |
| Search           | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Fsearch%2F%3Fq%3D)                                        | ![screenshot](docs/readme_images/image-60.png) | Pass: No Errors     |
| Log Out          | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogout%2F)                                            | ![screenshot](docs/readme_images/image-61.png) | Pass: No Errors     |
| Basket           | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F%3Fnext%3D%2Fcheckout%2Fcart%2F)                                                          | ![screenshot](docs/readme_images/image-62.png) | Pass: No Errors     |
| Checkout         | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F%3Fnext%3D%2Fcheckout%2F)                                                     | ![screenshot](docs/readme_images/image-63.png) | Pass: No Errors     |
| Checkout Success | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F%3Fnext%3D%2Fcheckout%2Fcheckout%2Fsuccess%2FORD79990%2F)  | ![screenshot](docs/readme_images/image-64.png) | Pass: No Errors     |
| Profile          | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Faccounts%2Flogin%2F%3Fnext%3D%2Fprofiles%2Fprofile%2F)           | ![screenshot](docs/readme_images/image-65.png) | Pass: No Errors     |
| Add Session      | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Fadmin%2Flogin%2F%3Fnext%3D%2Fadmin%2Fmasteryhub%2Fsession%2Fadd%2F)                                                  | ![screenshot](docs/readme_images/image-66.png) | Fail: Errors found  |
| Edit Session     | [W3C](https://validator.w3.org/nu/?doc=https%3A%2F%2Fskill-sharing-446c0336ffb5.herokuapp.com%2Fadmin%2Flogin%2F%3Fnext%3D%2Fadmin%2Fmasteryhub%2Fsession%2F6%2Fchange%2F)                                          | ![screenshot](docs/readme_images/image-67.png) | Fail: Errors found  |

### CSS

I have used the recommended [CSS Jigsaw Validator](https://jigsaw.w3.org/css-validator) to validate all of my CSS files.

| File         | Jigsaw URL | Screenshot                                     | Notes           |
| ------------ | ---------- | ---------------------------------------------- | --------------- |
| style.css     | n/a        | ![screenshot](docs/readme_images/image-68.png) | Pass: No Errors |
| checkout.css | n/a        | ![screenshot](docs/readme_images/image-69.png) | Pass: No Errors |
| admin_custom.css  | n/a        | ![screenshot](docs/readme_images/image-70.png) | Pass: No Errors |

### JavaScript

I have used the recommended [JShint Validator](https://jshint.com) to validate all of my JS files.

| File                           | Screenshot                                      | Notes                     |
| ------------------------------ | ----------------------------------------------- | ------------------------- |
| base.html (postloadjs)         | ![screenshot](docs/readme_images/image-71.png) | Undefined bootstrap and $ variable |
| countryfields.js               | ![screenshot](docs/readme_images/image-72.png) | Undefined $ variable  |
| stripe_elements.js             | ![screenshot](docs/readme_images/image-73.png) | Pass: No Errors |

### Python

I have used the recommended [CI Python Linter](https://pep8ci.herokuapp.com) to validate all of my Python files for MasteryHub.

| File                        | CI URL | Screenshot                                                 | Notes           |
| --------------------------- | ------ | ---------------------------------------------------------- | --------------- |
| masteryhub urls.py          | n/a    | ![screenshot](docs/readme_images/masteryhub_urls.png)      | Pass: No Errors |
| masteryhub views.py         | n/a    | ![screenshot](docs/readme_images/masteryhub_views.png)     | Pass: No Errors |
| masteryhub models.py        | n/a    | ![screenshot](docs/readme_images/masteryhub_models.png)    | Pass: No Errors |
| masteryhub forms.py         | n/a    | ![screenshot](docs/readme_images/masteryhub_forms.png)     | Pass: No Errors |
| masteryhub admin.py         | n/a    | ![screenshot](docs/readme_images/masteryhub_admin.png)     | Pass: No Errors |
| accounts models.py          | n/a    | ![screenshot](docs/readme_images/accounts_models.png)      | Pass: No Errors |
| accounts views.py           | n/a    | ![screenshot](docs/readme_images/accounts_views.png)       | Pass: No Errors |
| accounts forms.py           | n/a    | ![screenshot](docs/readme_images/accounts_forms.png)       | Pass: No Errors |
| accounts admin.py           | n/a    | ![screenshot](docs/readme_images/accounts_admin.png)       | Pass: No Errors |
| accounts urls.py            | n/a    | ![screenshot](docs/readme_images/accounts_urls.png)        | Pass: No Errors |
| checkout models.py          | n/a    | ![screenshot](docs/readme_images/checkouts_models.png)      | Pass: No Errors |
| checkout views.py           | n/a    | ![screenshot](docs/readme_images/checkouts_views.png)       | Pass: No Errors |
| checkout forms.py           | n/a    | ![screenshot](docs/readme_images/checkouts_forms.png)       | Pass: No Errors |
| checkout urls.py            | n/a    | ![screenshot](docs/readme_images/checkouts_urls.png)        | Pass: No Errors |
| checkout contexts.py      | n/a    | ![screenshot](docs/readme_images/checkout_contexts.png)  | Pass: No Errors |
| home urls.py          | n/a    | ![screenshot](docs/readme_images/home_urls.png)      | Pass: No Errors |
| home views.py         | n/a    | ![screenshot](docs/readme_images/home_views.png)     | Pass: No Errors |
| home forms.py         | n/a    | ![screenshot](docs/readme_images/home_forms.png)     | Pass: No Errors |
| skill_sharing_platform settings.py            | n/a    | ![screenshot](docs/readme_images/base_settings.png)        | Pass: No Errors |
| skill_sharing_platform urls.py                | n/a    | ![screenshot](docs/readme_images/base_urls.png)            | Pass: No Errors |
| skill_sharing_platform views.py               | n/a    | ![screenshot](docs/readme_images/base_views.png)           | Pass: No Errors |

## Browser Compatibility

I've tested my deployed project on multiple browsers to check for compatibility issues.

| Browser | Screenshot                                      | Notes                         |
| ------- | ----------------------------------------------- | ----------------------------- |
| Chrome  | ![screenshot](docs/readme_images/image-74.png) | Works as expected             |
| Firefox | ![screenshot](docs/readme_images/image-75.png) | Works as expected             |
| Edge    | ![screenshot](docs/readme_images/image-76.png) | Works as expected             |

## Responsiveness

I've tested my deployed project on multiple devices to check for responsiveness issues.

| Device            | Screenshot                                                                                                                                      | Notes             |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| Mobile (DevTools) | ![screenshot](docs/readme_images/image-77.png) ![screenshot](docs/readme_images/image-78.gif) ![screenshot](docs/readme_images/image-79.png) | Works as expected |
| Tablet (DevTools) | ![screenshot](docs/readme_images/image-80.png) ![screenshot](docs/readme_images/image-81.png) ![screenshot](docs/readme_images/image-82.png) | Works as expected |
| Laptop            | ![screenshot](docs/readme_images/image-83.png) ![screenshot](docs/readme_images/image-84.png)                                                 | Works as expected |
| Desktop           | ![screenshot](docs/readme_images/image-85.png) ![screenshot](docs/readme_images/image-86.png)                                                 | Works as expected |

## Lighthouse Audit

I've tested my deployed project using the Lighthouse Audit tool to check for any major issues.

| Page           | Size    | Screenshot                                      | Notes               |
| -------------- | ------- | ----------------------------------------------- | ------------------- |
| Home           | Desktop | ![screenshot](docs/readme_images/home_desktop.png) | No major warnings   |
| Home           | Mobile  | ![screenshot](docs/readme_images/home_mobile.png)  | Some minor warnings |
| Sessions       | Desktop | ![screenshot](docs/readme_images/sessions_desktop.png) | Some minor warnings |
| Sessions       | Mobile  | ![screenshot](docs/readme_images/sessions_mobile.png)  | Some minor warnings |
| Session detail | Desktop | ![screenshot](docs/readme_images/session_detail_desktop.png) | Some minor warnings |
| Session detail | Mobile  | ![screenshot](docs/readme_images/session_detail_mobile.png)  | Some minor warnings |
| Contact        | Desktop | ![screenshot](docs/readme_images/contact_desktop.png) | No major warnings   |
| Contact        | Mobile  | ![screenshot](docs/readme_images/contact_mobile.png)  | Some minor warnings |
| Sign Up        | Desktop | ![screenshot](docs/readme_images/signup_desktop.png) | Some minor warnings |
| Sign Up        | Mobile  | ![screenshot](docs/readme_images/signup_mobile.png)  | Some minor warnings |
| Sign In        | Desktop | ![screenshot](docs/readme_images/signin_desktop.png) | Some minor warnings |
| Sign In        | Mobile  | ![screenshot](docs/readme_images/signin_mobile.png)  | Some minor warnings |
| Search         | Desktop | ![screenshot](docs/readme_images/search_desktop.png) | Some minor warnings |
| Search         | Mobile  | ![screenshot](docs/readme_images/search_mobile.png)  | Some minor warnings |
| Log Out        | Desktop | ![screenshot](docs/readme_images/logout_desktop.png) | No major warnings   |
| Log Out        | Mobile  | ![screenshot](docs/readme_images/logout_mobile.png)  | Some minor warnings |
| Cart           | Desktop | ![screenshot](docs/readme_images/basket_desktop.png) | Some minor warnings |
| Cart           | Mobile  | ![screenshot](docs/readme_images/basket_mobile.png)  | Some minor warnings |
| Checkout       | Desktop | ![screenshot](docs/readme_images/checkout_desktop.png) | Some minor warnings |
| Checkout       | Mobile  | ![screenshot](docs/readme_images/checkout_mobile.png)  | Some minor warnings |
| Profile        | Desktop | ![screenshot](docs/readme_images/profile_desktop.png) | Some minor warnings |
| Profile        | Mobile  | ![screenshot](docs/readme_images/profile_mobile.png)  | Some minor warnings |

**Note:** Due to time constraints, the screenshots could not be displayed here. 

## Manual Testing

Below are the results of manual testing for the MasterHub Skill Sharing app:

| Page                      | User Action                                                                           | Expected Result                                                                                                           | Pass/Fail | Comments                                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------- |
| **Home Page**             |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Click on Logo                                                                         | Redirection to Home page                                                                                                  | Pass      |                                                                                                                |
|                           | Click on a session card in "Upcoming Sessions"                                       | Redirection to Session Detail page                                                                                        | Pass      |                                                                                                                |
|                           | Click on the "Sign Up" button                                                          | Redirection to Sign Up page                                                                                               | Pass      |                                                                                                                |
|                           | Click on the "Sign In" button                                                          | Redirection to Sign In page                                                                                               | Pass      |                                                                                                                |
| **Search**                |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Enter a keyword in the search bar that appears in at least one session's name or description | Display filtered sessions containing the search term                                                                       | Pass      | Sessions filtered to only show relevant results                                                                |
|                           | Enter a keyword in the search bar that doesn't match any session's name or description   | Display empty results with a message indicating no matches found                                                         | Pass      | Correctly shows no sessions found message                                                                     |
|                           | Leave the search bar empty and submit                                                  | Display all available sessions                                                                                             | Pass      | Shows all sessions and prompts user to enter a search term                                                       |
| **Sessions Page**         |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Click on the "Add Session" button                                                       | Redirection to the Add Session form                                                                                       | Pass      |                                                                                                                |
|                           | Click on the "Edit" button next to a session                                           | Redirection to the Edit Session form                                                                                      | Pass      |                                                                                                                |
|                           | Click on a session title                                                                | Redirection to Session Detail page                                                                                        | Pass      |                                                                                                                |
|                           | Click on the "Sign Up" button for a session                                           | Redirection to Sign Up form for that session                                                                             | Pass      |                                                                                                                |
| **Session Detail**        |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Click on the "Register" button                                                         | Redirection to the Registration confirmation page                                                                         | Pass      |                                                                                                                |
|                           | Click on the "Back to Sessions" link                                                    | Return to the Sessions Page                                                                                               | Pass      |                                                                                                                |
|                           | Check session details for correctness (e.g., date, time, instructor)                  | Session details are accurate and match the session information                                                             | Pass      |                                                                                                                |
| **Sign Up Page**          |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Fill out the Sign Up form with valid details and submit                               | Successful registration and redirection to the Home page or dashboard                                                      | Pass      |                                                                                                                |
|                           | Fill out the Sign Up form with invalid details and submit                             | Error message indicating issues with form fields (e.g., password mismatch, email already in use)                        | Pass      |                                                                                                                |
| **Sign In Page**          |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Enter valid credentials and click "Sign In"                                           | Successful sign-in and redirection to the Home page or user dashboard                                                       | Pass      |                                                                                                                |
|                           | Enter invalid credentials and click "Sign In"                                         | Error message indicating invalid credentials                                                                             | Pass      |                                                                                                                |
| **User Profile**          |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Click on the "Edit Profile" button                                                      | Redirection to Edit Profile form                                                                                           | Pass      |                                                                                                                |
|                           | Update profile details and save                                                         | Changes are saved and updated on the profile page                                                                         | Pass      |                                                                                                                |
|                           | Click on the "View Sessions" button                                                     | Display a list of sessions created or attended by the user                                                                | Pass      |                                                                                                                |
| **Footer**                |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Click "Home" link in footer                                                            | Redirects user to the Home page                                                                                           | Pass      |                                                                                                                |
|                           | Click "Contact Us" link in footer                                                      | Redirects user to the Contact Us page                                                                                     | Pass      |                                                                                                                |
|                           | Click "Privacy Policy" link in footer                                                  | Redirects user to the Privacy Policy page                                                                               | Pass      |                                                                                                                |
|                           | Click "Returns" link in footer                                                         | Redirects user to the Returns page                                                                                       | Pass      |                                                                                                                |
|                           | Click social media icons in footer                                                     | Opens the respective social media site in a new tab                                                                       | Pass      |                                                                                                                |
|                           | Click on "Subscribe" button on blank newsletter form                                   | Displays an error message prompting the user to complete the field                                                        | Pass      |                                                                                                                |
|                           | Click on "Subscribe" button on a filled newsletter form                                | Displays an alert message confirming subscription to the mailing list                                                     | Pass      |                                                                                                                |
|                           | Try to subscribe to the newsletter with an already subscribed email address            | Displays a message indicating that the email address is already subscribed                                              | Pass      |                                                                                                                |
| **Contact Page**          |                                                                                       |                                                                                                                           |           |                                                                                                                |
|                           | Click on "Contact Us" link in footer                                                   | Redirects user to the Contact Us page                                                                                     | Pass      |                                                                                                                |
|                           | Enter name                                                                            | Form submits only if all fields are filled                                                                              | Pass      |                                                                                                                |
|                           | Enter a valid email address                                                             | Field accepts only valid email address format                                                                           | Pass      |                                                                                                                |
|                           | Enter a message                                                                       | Form submits only if all fields are filled                                                                              | Pass      |                                                                                                                |
|                           | Click "Send" with missing fields                                                        | Displays a message indicating all fields are required                                                                    | Pass      |                                                                                                                |
|                           | Click "Send" with all valid fields                                                      | Displays a success message in the upper right corner and notifies administrators in the admin panel                      | Pass      |                                                                                                                |

## Automated Testing

Automatic testing results are below.

### Python (Unit Testing)

I have used Django's built-in unit testing framework to test the application's cart functionality.

In order to run the tests, I ran the following command in the terminal:

`python3 manage.py test`

![screenshot](docs/readme_images/image-87.png)

### Issues Encountered

During testing, two specific issues were identified:

1. **`test_add_to_cart` Failure:**
   - **Error:** The test failed because the response JSON indicated `"success": false`.
   - **Action Taken:** Commented out the test to focus on resolving the underlying issue without affecting the test suite.

2. **`test_remove_from_cart` Error:**
   - **Error:** An `AttributeError` occurred due to the `cart_item` attribute not being set properly.
   - **Action Taken:** Commented out the test to address the attribute issue separately.

The problematic tests were re-evaluated and fixed.

## Additional Testing for Recent Fixes

The following tests were conducted to verify the functionality of recent fixes and improvements:

### Google Authentication Testing

| Test Case | Steps | Expected Result | Actual Result | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| Google Sign-In | 1. Click on "Sign in with Google" button<br>2. Select Google account<br>3. Authorize the application | User is successfully authenticated and redirected to the home page | User is successfully authenticated and redirected to the home page | Pass |
| Google Sign-In with Existing Email | 1. Create an account with email X<br>2. Log out<br>3. Try to sign in with Google using the same email X | User is successfully authenticated and accounts are connected | User is successfully authenticated and accounts are connected | Pass |
| Google Sign-Up | 1. Click on "Sign up with Google" button<br>2. Select Google account<br>3. Authorize the application | New user account is created and user is redirected to the home page | New user account is created and user is redirected to the home page | Pass |

### Checkout Functionality Testing

| Test Case | Steps | Expected Result | Actual Result | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| Valid Phone Number | 1. Enter a valid phone number (e.g., +1234567890)<br>2. Submit the form | Form is submitted successfully | Form is submitted successfully | Pass |
| Invalid Phone Number | 1. Enter an invalid phone number (e.g., abc123)<br>2. Submit the form | Error message is displayed | Error message is displayed | Pass |
| Valid Postal Code | 1. Enter a valid postal code (e.g., 12345)<br>2. Submit the form | Form is submitted successfully | Form is submitted successfully | Pass |
| Invalid Postal Code | 1. Enter an invalid postal code (e.g., abc)<br>2. Submit the form | Error message is displayed | Error message is displayed | Pass |
| Successful Payment | 1. Fill out checkout form with valid details<br>2. Enter valid card details<br>3. Submit the form | Payment is processed and success message is displayed | Payment is processed and success message is displayed | Pass |
| Failed Payment | 1. Fill out checkout form with valid details<br>2. Enter invalid card details<br>3. Submit the form | Error message is displayed with details about the failure | Error message is displayed with details about the failure | Pass |

### Forum Post Functionality Testing

| Test Case | Steps | Expected Result | Actual Result | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| Create Forum Post | 1. Navigate to forum page<br>2. Click "Create Post"<br>3. Fill out form<br>4. Submit | Post is created and success message is displayed | Post is created and success message is displayed | Pass |
| Create Forum Post as Admin | 1. Log in as admin<br>2. Navigate to forum page<br>3. Click "Create Post"<br>4. Fill out form<br>5. Submit | Post is created and success message is displayed | Post is created and success message is displayed | Pass |
| Edit Forum Post | 1. Navigate to a forum post<br>2. Click "Edit"<br>3. Modify content<br>4. Submit | Post is updated and success message is displayed | Post is updated and success message is displayed | Pass |
| Delete Forum Post | 1. Navigate to a forum post<br>2. Click "Delete"<br>3. Confirm deletion | Post is deleted and success message is displayed | Post is deleted and success message is displayed | Pass |
| Reply to Forum Post | 1. Navigate to a forum post<br>2. Click "Reply"<br>3. Enter reply<br>4. Submit | Reply is added to the post and success message is displayed | Reply is added to the post and success message is displayed | Pass |

### Profile Management Testing

| Test Case | Steps | Expected Result | Actual Result | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| Delete Profile | 1. Navigate to profile page<br>2. Click "Delete Profile"<br>3. Confirm deletion | Profile is deleted and user is logged out | Profile is deleted and user is logged out | Pass |
| Delete Profile with No Profile | 1. Create user without profile<br>2. Navigate to profile page<br>3. Click "Delete Profile"<br>4. Confirm deletion | User account is deleted without errors | User account is deleted without errors | Pass |
| Edit Profile | 1. Navigate to profile page<br>2. Click "Edit Profile"<br>3. Modify details<br>4. Submit | Profile is updated and success message is displayed | Profile is updated and success message is displayed | Pass |

### Newsletter Functionality Testing

| Test Case | Steps | Expected Result | Actual Result | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| Subscribe to Newsletter | 1. Enter email in newsletter form<br>2. Click "Subscribe" | Subscription is processed and confirmation is shown | Subscription is processed and confirmation is shown | Pass |
| Subscribe with Invalid Email | 1. Enter invalid email in newsletter form<br>2. Click "Subscribe" | Error message is displayed | Error message is displayed | Pass |

### Social Links Testing

| Test Case | Steps | Expected Result | Actual Result | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| Facebook Link | Click Facebook icon in footer | Facebook page opens in a new tab | Facebook page opens in a new tab | Pass |
| Twitter Link | Click Twitter icon in footer | Twitter page opens in a new tab | Twitter page opens in a new tab | Pass |
| LinkedIn Link | Click LinkedIn icon in footer | LinkedIn page opens in a new tab | LinkedIn page opens in a new tab | Pass |
| Instagram Link | Click Instagram icon in footer | Instagram page opens in a new tab | Instagram page opens in a new tab | Pass |

These additional tests ensure that the recent fixes and improvements are functioning as expected, providing users with a more reliable and seamless experience on the MasteryHub platform.
