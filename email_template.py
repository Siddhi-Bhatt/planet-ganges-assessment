# email_template.py
# Builds the HTML email body. Kept as a separate module so it's
# easy to redesign or swap to a templating engine (Jinja2, etc.) later.
BAND_COLORS = {
    "High":   {"bg": "#E1F5EE", "text": "#085041", "badge": "#1D9E75"},
    "Medium": {"bg": "#FAEEDA", "text": "#412402", "badge": "#BA7517"},
    "Low":    {"bg": "#FCEBEB", "text": "#501313", "badge": "#E24B4A"},
}


def _dimension_block(dim: dict) -> str:
    colors = BAND_COLORS.get(dim["band"], BAND_COLORS["Low"])
    bar_pct = dim["percentage"]

    return f"""
    <tr>
      <td style="padding: 0 0 24px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding-bottom: 8px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="font-family: Georgia, serif; font-size: 16px; font-weight: bold; color: #1A1A2E;">
                    {dim["label"]}
                  </td>
                  <td align="right">
                    <span style="
                      display: inline-block;
                      background: {colors['badge']};
                      color: #ffffff;
                      font-family: Arial, sans-serif;
                      font-size: 12px;
                      font-weight: bold;
                      padding: 4px 12px;
                      border-radius: 20px;
                    ">{dim["band"]}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom: 4px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="background: #EEEEEE; border-radius: 4px; height: 8px;">
                <tr>
                  <td width="{bar_pct}%" style="
                    background: {colors['badge']};
                    border-radius: 4px;
                    height: 8px;
                    font-size: 0;
                    line-height: 0;
                  ">&nbsp;</td>
                  <td width="{100 - bar_pct}%">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="
              font-family: Arial, sans-serif;
              font-size: 11px;
              color: #888888;
              padding-bottom: 10px;
            ">{dim["score"]} / {dim["max_score"]} &nbsp;·&nbsp; {bar_pct}%</td>
          </tr>
          <tr>
            <td style="
              background: {colors['bg']};
              border-left: 3px solid {colors['badge']};
              border-radius: 0 4px 4px 0;
              padding: 12px 16px;
            ">
              <p style="
                font-family: Arial, sans-serif;
                font-size: 13px;
                line-height: 1.6;
                color: {colors['text']};
                margin: 0;
              ">{dim["feedback"]}</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def build_email_html(name: str, scores: dict) -> str:
    dimension_blocks = "".join(_dimension_block(d) for d in scores["dimensions"])
    total = scores["total_score"]
    total_max = scores["total_max"]
    pct = scores["overall_percentage"]

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Leadership Assessment Report</title>
</head>
<body style="margin: 0; padding: 0; background: #F5F4F0; font-family: Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #F5F4F0; padding: 40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width: 600px; width: 100%; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #E0DED8;">

          <!-- Header -->
          <tr>
            <td style="background: #1A1A2E; padding: 32px 40px;">
              <p style="margin: 0 0 4px 0; font-family: Arial, sans-serif; font-size: 11px;
                        letter-spacing: 2px; text-transform: uppercase; color: #8888AA;">
                Planet Ganges Consulting
              </p>
              <h1 style="margin: 0; font-family: Georgia, serif; font-size: 26px;
                         font-weight: normal; color: #ffffff;">
                Leadership Assessment
              </h1>
            </td>
          </tr>

          <!-- Intro -->
          <tr>
            <td style="padding: 32px 40px 24px 40px; border-bottom: 1px solid #EEEEEE;">
              <p style="margin: 0 0 8px 0; font-size: 15px; color: #1A1A2E;">
                Hi <strong>{name}</strong>,
              </p>
              <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #555555;">
                Thank you for completing the leadership self-assessment. Here's a summary of your
                results across three key leadership dimensions. A full PDF report is attached for
                your records.
              </p>
            </td>
          </tr>

          <!-- Overall score -->
          <tr>
            <td style="padding: 24px 40px; background: #F5F4F0; border-bottom: 1px solid #EEEEEE;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <p style="margin: 0 0 4px 0; font-size: 11px; text-transform: uppercase;
                              letter-spacing: 1px; color: #888888;">Overall Score</p>
                    <p style="margin: 0; font-size: 28px; font-weight: bold; color: #1A1A2E;
                              font-family: Georgia, serif;">{total} <span style="font-size: 16px; color: #888888;">/ {total_max}</span></p>
                  </td>
                  <td align="right">
                    <div style="
                      width: 64px; height: 64px; border-radius: 50%;
                      background: #534AB7; color: white;
                      font-size: 18px; font-weight: bold;
                      text-align: center; line-height: 64px;
                      display: inline-block;
                    ">{pct}%</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Dimension results -->
          <tr>
            <td style="padding: 32px 40px 8px 40px;">
              <h2 style="margin: 0 0 20px 0; font-family: Georgia, serif; font-size: 18px;
                         font-weight: normal; color: #1A1A2E;">Your Dimension Scores</h2>
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {dimension_blocks}
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background: #F5F4F0; padding: 24px 40px; border-top: 1px solid #EEEEEE;">
              <p style="margin: 0; font-size: 12px; color: #AAAAAA; text-align: center;">
                This report was generated by the Planet Ganges Leadership Assessment Platform.<br>
                Please keep this email for your records.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""