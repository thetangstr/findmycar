# Enable Firebase Storage

To enable Firebase Storage for your project, please follow these steps:

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `findmycar-347ec`
3. In the left sidebar, click on "Storage"
4. Click "Get Started" to enable Firebase Storage
5. Select a location for your Storage bucket (choose the region closest to your users)
6. Accept the default security rules or use the ones we've already defined in `storage.rules`
7. Click "Done" to complete the setup

After enabling Firebase Storage, you can run the image upload script again:

```bash
./scripts/upload-images.sh
```

This will upload the vehicle images to Firebase Storage and store their URLs in Firestore.
