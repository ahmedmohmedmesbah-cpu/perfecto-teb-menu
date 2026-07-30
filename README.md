# Perfecto Tebo Digital Menu

Static Arabic RTL digital menu for Perfecto. It displays products and prices only. There is no cart, checkout, customer account system, backend, or paid service.

## Project Structure

```text
assets/
  css/styles.css
  images/storefront-hero.png
  images/products/
  js/app.js
data/products.json
python_editor/main.py
index.html
category.html
README.md
```

## Update Products

1. Install the required Python dependency if needed:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the desktop editor:

   ```bash
   python python_editor/main.py
   ```

3. Add or edit categories and products.
4. Use the Excel import/export buttons for bulk price and unit updates.
5. Click `Save JSON`.
6. Commit and push the updated files to GitHub.

The website reads from `data/products.json`, so non-technical updates do not require editing HTML, CSS, or JavaScript.

## Product Images

Images are optional. If a product has no image, the website shows a clean category placeholder. The editor can copy selected product images into:

```text
assets/images/products/
```

Use relative image paths in JSON, for example:

```text
assets/images/products/rice.jpg
```

## GitHub Pages

Host this project for free with GitHub Pages:

1. Push the project to a GitHub repository.
2. Open repository `Settings`.
3. Go to `Pages`.
4. Choose the main branch and root folder.
5. Save.

GitHub Pages will serve `index.html` automatically.

## Notes

- The real storefront photo is saved in `assets/images/storefront-hero.png`.
- The clean logo used by the website is saved in `assets/images/logo.png`.
- Replace these files later with higher-resolution official assets if needed, keeping the same filenames.
- The site is intentionally vanilla HTML, CSS, and JavaScript for simple free hosting.
