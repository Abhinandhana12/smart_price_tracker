
import os
import sendgrid
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = "@API KEY@"
FROM_EMAIL = "@FROM EMAIL@"

def send_alert(to_email, product_name, current_price, target_price, url):
    """Send a price drop alert email via SendGrid."""
    if not SENDGRID_API_KEY:
        print(f"[ALERT] Price dropped for {product_name}: ₹{current_price} (target: ₹{target_price})")
        print(f"  → Would send email to {to_email}")
        return

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=f'🎯 Price Drop Alert: {product_name}',
        html_content=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #10b981;">🎉 Price Drop Detected!</h2>
            <p>Great news! The price of <strong>{product_name}</strong> has dropped below your target.</p>
            <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                <tr style="background:#f3f4f6;">
                    <td style="padding:12px; border:1px solid #e5e7eb;">Current Price</td>
                    <td style="padding:12px; border:1px solid #e5e7eb; color:#10b981; font-weight:bold;">₹{current_price:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding:12px; border:1px solid #e5e7eb;">Your Target Price</td>
                    <td style="padding:12px; border:1px solid #e5e7eb;">₹{target_price:,.2f}</td>
                </tr>
                <tr style="background:#f3f4f6;">
                    <td style="padding:12px; border:1px solid #e5e7eb;">You Save</td>
                    <td style="padding:12px; border:1px solid #e5e7eb; color:#059669; font-weight:bold;">₹{target_price - current_price:,.2f}</td>
                </tr>
            </table>
            <a href="{url}" style="display:inline-block; background:#10b981; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:bold;">
                Buy Now →
            </a>
            <p style="color:#6b7280; margin-top:20px; font-size:13px;">This alert was sent by Smart Price Tracker.</p>
        </div>
        """
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email} | Status: {response.status_code}")
    except Exception as e:
        print(f"Email error: {e}")


