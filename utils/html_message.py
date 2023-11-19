style = """
.backgroundTable {
        margin: 0 auto;
        padding: 0;
        width: 100% !important;
      }
      .ReadMsgBody {
        width: 100%;
      }
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      body {
        -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
        width: 100% !important;
        margin: 0;
        padding: 0;
        -webkit-font-smoothing: antialiased !important;
      }
      table {
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
      }
      table td {
        border-collapse: collapse;
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
        padding: 0;
      }
      img {
        -ms-interpolation-mode: bicubic;
        width: 100%;
        display: block;
      }
      a img {
        border: none;
      }
      p {
        margin: 0;
      }
      a {
        text-decoration: none !important;
      }
      .appleBody a {
        color: #68440a;
        text-decoration: none;
      }
      .appleFooter a {
        color: #999999;
        text-decoration: none;
      }
      a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
      }
      @media only screen and (max-width: 480px) {
        .column {
          display: table !important;
          width: 100% !important;
        }
        .t-left {
          text-align: left !important;
        }
        .pb-16 {
          padding: 0 0 16px 0 !important;
        }
      }
      .meter-bar {
        width: 100%;
        height: 10px;
        border-radius: 4px;
      }
      .meter-bar-fill {
        height: 8px;
        border-radius: 4px;
        height: 100%;
      }
      .clearbit-img:before {
        content: " ";
        display: block;
        position: absolute;
        height: 40px;
        width: 40px;
        background-color: white;
        /*background-image: url("https://via.placeholder.com/40.png/000000/FFFFFF/?text=Prima Coffee");*/
      }
      .alert {
        font-family: montserrat;
        border-radius: 4px;
        padding: 15px 20px;
      }
      .alert.alert-sm {
        padding: 5px 15px;
        font-size: 12px;
      }
      .alert-warning {
        background-color: #fff3cd;
        border-color: #ffeeba;
        border-width: thin;
        border-style: solid;
        color: #856404;
      }
"""

template_1st_half = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title></title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="format-detection" content="telephone=no" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1.0 maximum-scale=1.0; user-scalable=no;"
    />
    <style>
      {style}
    </style>
  </head>
  <body
    leftmargin="0"
    marginwidth="0"
    topmargin="0"
    marginheight="0"
    offset="0"
  >
    <table
      width="100%"
      cellspacing="0"
      cellpadding="0"
      border="0"
      bgcolor="#F0F2F5"
    >
      <tr>
        <td align="center" style="padding: 40px 0">
          <a href="#" target="_blank"
            ><img
              src="https://lairesit.sirv.com/Images/Zephyrus%20logo.png"
              width="48"
              style="max-width: 48px"
              alt="Fast"
          /></a>
        </td>
      </tr>
      <tr>
        <td style="padding: 0 12px" align="center">
          <!--[if mso]><table width="420" cellspacing="0" cellpadding="0" border="0" align="center"><![endif]-->

          <!--[if !mso]>

<!-->
          <table
            cellspacing="0"
            cellpadding="0"
            border="0"
            align="center"
            style="width: 100%; max-width: 420px"
          >
            <!--<![endif]-->

            <!--- Top Card -->
            <tr>
              <td class="pb-16" style="padding: 0 0 24px 0">
                <table
                  width="100%"
                  cellspacing="0"
                  cellpadding="0"
                  border="0"
                  bgcolor="#FFFFFF"
                  style="border-radius: 6px 6px 0 0"
                >
                  <tr>
                    <td style="padding: 28px 0px 0px 24px">
                      <p
                        style="
                          font: 400 16px Inter, Helvetica, Arial, sans-serif;
                          color: #000000;
                          line-height: 160%;
                        "
                      >
                        Registration #{reg_id}
                      </p>
                    </td>
                  </tr>
                </table>
                <table
                  width="100%"
                  cellspacing="0"
                  cellpadding="0"
                  border="0"
                  bgcolor="#FFFFFF"
                  style="border-radius: 6px 6px 0 0"
                >
                  <tr>
                    <td style="padding: 28px 24px">
                      <p
                        style="
                          font: bold 18px Helvetica, Arial, sans-serif;
                          color: #000000;
                        "
                      >
                        Hi {name},
                      </p>
                    </td>
                    <td style="padding: 28px 32px 24px 24px" align="right">
                      <img
                        class="clearbit-img"
                        src="{qrcode_url}"
                        style="
                          width: 90px;
                          height: 90px;
                          object-fit: scale-down;
                        "
                      />
                    </td>
                  </tr>
                </table>
                <table
                  width="100%"
                  cellspacing="0"
                  cellpadding="0"
                  border="0"
                  bgcolor="#FFFFFF"
                  style="border-radius: 0 0 6px 6px"
                >
                  <tr>
                    <td style="padding: 0px 24px 29px">
                      <p
                        style="
                          font: 400 16px Inter, Helvetica, Arial, sans-serif;
                          color: #000000;
                          line-height: 160%;
                        "
                      >
                        Great news! Your {event_name} registration is successful!
                        Show this QR code at the college entrance when you
                        arrive.
                        <br />
                        <br />
                      </p>
                      {spl_message}
                      <p style="line-height: 18px; font-size: 1px">&nbsp;</p>

                      <!--[if mso]><table width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#000000"><tr><td style="padding:11px 0;"><![endif]-->
                      <a
                        href="{reg_link}"
                        target="_blank"
                        style="
                          display: inline-block;
                          width: 100%;
                          line-height: 40px;
                          background-color: #000000;
                          border-radius: 8px;
                          font-size: 14px;
                          font-family: Helvetica, Arial, sans-serif;
                          color: #ffffff;
                          text-align: center;
                          font-weight: bold;
                        "
                      >
                        View Registration Details
                      </a>

                      <!--[if mso]></td></tr></table><![endif]-->
                      <p
                        style="
                          font: 400 12px Inter, Helvetica, Arial, sans-serif;
                          text-align: center;
                          line-height: 150%;
                          margin-top: 24px;
                          color: #474747;
                        "
                      >
                        You can view all your registration details on your
                        dashboard.
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- ::: ORDER ::: -->
            <tr>
              <td class="pb-16" style="padding: 0 0 24px 0">
                <table
                  width="100%"
                  cellspacing="0"
                  cellpadding="0"
                  border="0"
                  bgcolor="#FFFFFF"
                  style="border-radius: 6px"
                >
                  <tr>
                    <td style="padding: 27px 24px 24px 24px">
                      <p
                        style="
                          font: 16px Helvetica, Arial, sans-serif;
                          color: #000000;
                        "
                      >
                        Your Order
                      </p>
                      <p
                        style="
                          font: 12px Helvetica, Arial, sans-serif;
                          color: #474747;
                          margin-top: 10px;
                          margin-bottom: 10px;
                        "
                      >
                        Transaction No:: {txn_id}
                      </p>
                      <div
                        style="
                          margin: 16px 0;
                          height: 2px;
                          background-color: #f0f2f5;
                        "
                      ></div>

"""
template_2nd_half = """
<div
                        style="
                          margin: 16px 0;
                          height: 2px;
                          background-color: #f0f2f5;
                        "
                      ></div>

                      <!-- ::: TOTALS ::: -->
                      <table
                        width="100%"
                        cellspacing="0"
                        cellpadding="0"
                        border="0"
                      >
                        <tr>
                          <td
                            style="
                              padding: 16px 0 0 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                            "
                          >
                            Subtotal
                          </td>
                          <td
                            style="
                              padding: 16px 0 0 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                              text-align: right;
                            "
                          >
                            ₹{total}
                          </td>
                        </tr>
                        <tr>
                          <td
                            style="
                              padding: 16px 0 0 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                            "
                          >
                            Tax
                          </td>
                          <td
                            style="
                              padding: 16px 0 0 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                              text-align: right;
                            "
                          >
                            ₹{tax}
                          </td>
                        </tr>
                        <tr>
                          <td
                            style="
                              padding: 16px 0 0 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                            "
                          >
                            Discount
                          </td>
                          <td
                            style="
                              padding: 16px 0 0 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                              text-align: right;
                            "
                          >
                            ₹-{tax}
                          </td>
                        </tr>
                        <tr>
                          <td
                            style="
                              padding: 16px 0;
                              font: bold 16px Helvetica, Arial, sans-serif;
                              color: #000000;
                            "
                          >
                            Total (INR)
                          </td>
                          <td
                            style="
                              padding: 16px 0;
                              font: bold 16px Helvetica, Arial, sans-serif;
                              color: #000000;
                              text-align: right;
                            "
                          >
                            ₹{total}
                          </td>
                        </tr>
                      </table>
                      <div
                        style="
                          margin: 16px 0 32px;
                          height: 2px;
                          background-color: #f0f2f5;
                        "
                      ></div>

                      <!-- ::: DETAILS ::: -->
                      <table
                        width="100%"
                        cellspacing="0"
                        cellpadding="0"
                        border="0"
                      >
                        <tr>
                          <td
                            style="
                              padding: 0 0 24px 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                            "
                          >
                            {payment_mode}
                          </td>
                          <td
                            style="
                              padding: 0 0 24px 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                              text-align: right;
                            "
                          >
                            {txn_date}
                          </td>
                        </tr>
                        <tr>
                          <td
                            style="
                              padding: 0 0 24px 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                              min-width: 180px;
                              vertical-align: top;
                            "
                          >
                            {name}
                          </td>
                          <td
                            style="
                              padding: 0 0 24px 0;
                              font: 14px Helvetica, Arial, sans-serif;
                              color: #000000;
                              text-align: right;
                              line-height: 200%;
                            "
                          >
                            {address}
                          </td>
                        </tr>
                      </table>

                      <!-- ::: Bottom Desc ::: -->
                      <table>
                        <tr>
                          <td>
                            <p
                              style="
                                font: 14px Helvetica, Arial, sans-serif;
                                line-height: 20px;
                                text-align: center;
                                color: #474747;
                                padding: 0 16px;
                              "
                            >
                              Questions about your order? Please contact us
                              <br />or visit our
                              <a
                                href="https://instagram.com/techzephyrus/"
                                target="_blank"
                                style="color: #0286ff"
                                >Instagram page</a
                              >
                            </p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0 40px">
                <p
                  style="
                    font: 12px Helvetica, Arial, sans-serif;
                    color: #808080;
                    text-align: center;
                    line-height: 16px;
                  "
                >
                  © 2023 Christ College (Autonomous)
                  <br />
                  <br />
                  Christ Nagar, Irinjalakuda <br />
                  Thrissur, Kerala 680121
                  <br />
                  <br />
                  <a
                    href="mailto:cssfdept@christcollegeijk.edu.in"
                    target="_blank"
                    style="color: #1889fb"
                    >Contact Us</a
                  >&nbsp;&nbsp;&nbsp;<a
                    href="https://christcs.in/privacy/"
                    target="_blank"
                    style="color: #1889fb"
                    >Privacy Policy</a
                  >
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

pricing_row = """
<div style="display: table; width: 100%">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          border="0"
                        >
                          <tr>
                            <td width="64">
                              <img
                                src="{img}"
                                width="64"
                                style="max-width: 64px; border-radius: 4px"
                              />
                            </td>
                            <td style="padding: 0 17px">
                              <p
                                style="
                                  font: 14px Helvetica, Arial, sans-serif;
                                  color: #000000;
                                "
                              >
                                {program_name}
                              </p>
                            </td>
                            <td>
                              <p
                                style="
                                  font: 14px Helvetica, Arial, sans-serif;
                                  color: #000000;
                                  text-align: right;
                                "
                              >
                                ₹{fee}
                              </p>
                            </td>
                          </tr>
                        </table>
                        <p style="line-height: 16px; font-size: 1px">&nbsp;</p>
                      </div>
"""

special_message = """
                      <div class="alert alert-warning">
                        <p
                          style="
                            font: 400 16px Inter, Helvetica, Arial, sans-serif;
                            color: #000000;
                            line-height: 160%;
                          "
                        >
                        {message}
                        </p>
                      </div>
                      <br />
"""
