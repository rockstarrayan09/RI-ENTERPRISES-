from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

import config
from auth_utils import delete_upload, login_required, save_upload
from network_utils import get_local_ip
from database import (
    create_document,
    create_service,
    delete_document,
    delete_service,
    get_all_documents,
    get_all_services,
    get_document,
    get_documents_for_service,
    get_service,
    get_service_document_ids,
    init_db,
    update_document,
    update_service,
)
from excel_store import append_record, validate_submission

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

init_db()


@app.context_processor
def inject_company():
    local_ip = get_local_ip()
    network_url = f"http://{local_ip}:{config.PORT}"
    return {
        "company_name": config.COMPANY_NAME,
        "founder_name": config.FOUNDER_NAME,
        "company_tagline": config.COMPANY_TAGLINE,
        "network_url": network_url,
    }


@app.route("/uploads/certificates/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_DIR, filename)


@app.route("/")
def index():
    services = get_all_services()
    return render_template("index.html", services=services)


@app.route("/documents")
def documents_page():
    documents = get_all_documents()
    return render_template("documents.html", documents=documents)


@app.route("/service/<int:service_id>", methods=["GET", "POST"])
def service_detail(service_id):
    service = get_service(service_id)
    if not service:
        flash("Service not found.", "error")
        return redirect(url_for("index"))

    errors = []
    if request.method == "POST":
        errors, name, mobile, aadhaar = validate_submission(
            request.form.get("customer_name"),
            request.form.get("mobile"),
            request.form.get("aadhaar"),
        )
        if not errors:
            append_record(service["name"], service["amount"], name, mobile, aadhaar)
            flash("Customer details saved successfully to Excel.", "success")
            return redirect(url_for("service_detail", service_id=service_id))

    return render_template(
        "service_detail.html",
        service=service,
        required_documents=get_documents_for_service(service_id),
        errors=errors,
        form_data=request.form if request.method == "POST" else {},
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Welcome to the admin panel.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    services = get_all_services()
    documents = get_all_documents()
    return render_template(
        "admin/dashboard.html",
        services_count=len(services),
        documents_count=len(documents),
    )


@app.route("/admin/services", methods=["GET", "POST"])
@login_required
def admin_services():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            name = request.form.get("name", "").strip()
            amount_raw = request.form.get("amount", "").strip()
            image = request.files.get("image")

            if not name:
                flash("Service name is required.", "error")
            else:
                try:
                    amount = float(amount_raw)
                    if amount <= 0:
                        raise ValueError
                except ValueError:
                    flash("Amount must be a positive number.", "error")
                else:
                    filename, error = save_upload(image)
                    if error:
                        flash(error, "error")
                    else:
                        document_ids = request.form.getlist("document_ids")
                        create_service(name, amount, filename, document_ids)
                        flash("Service added successfully.", "success")

        elif action == "edit":
            service_id = request.form.get("service_id")
            name = request.form.get("name", "").strip()
            amount_raw = request.form.get("amount", "").strip()
            image = request.files.get("image")

            service = get_service(service_id)
            if not service:
                flash("Service not found.", "error")
            elif not name:
                flash("Service name is required.", "error")
            else:
                try:
                    amount = float(amount_raw)
                    if amount <= 0:
                        raise ValueError
                except ValueError:
                    flash("Amount must be a positive number.", "error")
                else:
                    new_filename = None
                    if image and image.filename:
                        new_filename, error = save_upload(image)
                        if error:
                            flash(error, "error")
                            return redirect(url_for("admin_services"))
                        delete_upload(service.get("image_filename"))

                    update_service(
                        service_id,
                        name,
                        amount,
                        new_filename,
                        request.form.getlist("document_ids"),
                    )
                    flash("Service updated successfully.", "success")

        elif action == "delete":
            service_id = request.form.get("service_id")
            service = get_service(service_id)
            if service:
                delete_upload(service.get("image_filename"))
                delete_service(service_id)
                flash("Service deleted successfully.", "success")
            else:
                flash("Service not found.", "error")

        return redirect(url_for("admin_services"))

    services = get_all_services()
    all_documents = get_all_documents()
    service_documents = {
        service["id"]: get_service_document_ids(service["id"]) for service in services
    }
    return render_template(
        "admin/services.html",
        services=services,
        all_documents=all_documents,
        service_documents=service_documents,
    )


@app.route("/admin/documents", methods=["GET", "POST"])
@login_required
def admin_documents():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            is_mandatory = request.form.get("is_mandatory") == "1"

            if not name:
                flash("Document name is required.", "error")
            else:
                create_document(name, description, is_mandatory)
                flash("Document added successfully.", "success")

        elif action == "edit":
            document_id = request.form.get("document_id")
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            is_mandatory = request.form.get("is_mandatory") == "1"

            document = get_document(document_id)
            if not document:
                flash("Document not found.", "error")
            elif not name:
                flash("Document name is required.", "error")
            else:
                update_document(document_id, name, description, is_mandatory)
                flash("Document updated successfully.", "success")

        elif action == "delete":
            document_id = request.form.get("document_id")
            document = get_document(document_id)
            if document:
                delete_document(document_id)
                flash("Document deleted successfully.", "success")
            else:
                flash("Document not found.", "error")

        return redirect(url_for("admin_documents"))

    documents = get_all_documents()
    return render_template("admin/documents.html", documents=documents)


if __name__ == "__main__":
    import threading
    import webbrowser

    local_ip = get_local_ip()
    local_url = f"http://127.0.0.1:{config.PORT}"
    network_url = f"http://{local_ip}:{config.PORT}"

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    (config.DATA_DIR / "share-link.txt").write_text(
        f"On this PC: {local_url}\n"
        f"On phone / other device (same Wi-Fi): {network_url}\n",
        encoding="utf-8",
    )

    print("=" * 48)
    print("  RI ENTERPRISES website is running")
    print("=" * 48)
    print(f"  This PC:     {local_url}")
    print(f"  Phone/Other: {network_url}")
    print("  Use the Phone/Other link on mobile (same Wi-Fi).")
    print("  Press Ctrl+C to stop.")
    print("=" * 48)

    if not config.AUTOSTART:

        def open_browser():
            webbrowser.open(local_url)

        threading.Timer(1.5, open_browser).start()

    app.run(
        debug=config.FLASK_DEBUG,
        host=config.HOST,
        port=config.PORT,
        use_reloader=not config.AUTOSTART,
    )
