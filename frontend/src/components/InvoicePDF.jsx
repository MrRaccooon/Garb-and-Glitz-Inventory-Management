import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

const generateInvoicePDF = (saleData) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  
  // Header - Company Name
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text('Garb & Glitz', pageWidth / 2, 20, { align: 'center' });
  
  // Company Details
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text('123 Fashion Street, Mumbai, Maharashtra 400001', pageWidth / 2, 28, { align: 'center' });
  doc.text('Phone: +91 9876543210 | Email: sales@garbglitz.com', pageWidth / 2, 34, { align: 'center' });
  
  // Line separator
  doc.setLineWidth(0.5);
  doc.line(15, 40, pageWidth - 15, 40);
  
  // Invoice Details
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('INVOICE', 15, 50);
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  const invoiceNumber = saleData.invoice_number || `INV-${saleData.id || Date.now()}`;
  const invoiceDate = new Date(saleData.date || Date.now()).toLocaleDateString('en-IN');
  
  doc.text(`Invoice #: ${invoiceNumber}`, 15, 58);
  doc.text(`Date: ${invoiceDate}`, 15, 64);
  doc.text(`Payment Mode: ${saleData.payment_mode || 'Cash'}`, 15, 70);
  
  // Items Table
  const tableStartY = 80;
  const tableData = saleData.items.map(item => {
    const itemTotal = item.price * item.quantity;
    const discountAmount = (itemTotal * (item.discount || 0)) / 100;
    const finalTotal = itemTotal - discountAmount;
    
    return [
      item.name || item.product_name || 'Item',
      item.quantity.toString(),
      `₹${item.price.toFixed(2)}`,
      `${item.discount || 0}%`,
      `₹${finalTotal.toFixed(2)}`
    ];
  });
  
  doc.autoTable({
    startY: tableStartY,
    head: [['Item', 'Qty', 'Price', 'Discount', 'Total']],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [41, 128, 185],
      textColor: 255,
      fontStyle: 'bold',
      halign: 'left'
    },
    columnStyles: {
      0: { cellWidth: 80 },
      1: { halign: 'center', cellWidth: 20 },
      2: { halign: 'right', cellWidth: 30 },
      3: { halign: 'center', cellWidth: 25 },
      4: { halign: 'right', cellWidth: 30 }
    },
    styles: {
      fontSize: 10,
      cellPadding: 4
    },
    margin: { left: 15, right: 15 }
  });
  
  // Summary Section
  const finalY = doc.lastAutoTable.finalY + 10;
  const summaryX = pageWidth - 70;
  
  doc.setFontSize(10);
  doc.text('Subtotal:', summaryX, finalY);
  doc.text(`₹${saleData.subtotal.toFixed(2)}`, pageWidth - 20, finalY, { align: 'right' });
  
  // GST Breakdown
  const cgst = (saleData.gst / 2).toFixed(2);
  const sgst = (saleData.gst / 2).toFixed(2);
  
  doc.text('CGST (9%):', summaryX, finalY + 6);
  doc.text(`₹${cgst}`, pageWidth - 20, finalY + 6, { align: 'right' });
  
  doc.text('SGST (9%):', summaryX, finalY + 12);
  doc.text(`₹${sgst}`, pageWidth - 20, finalY + 12, { align: 'right' });
  
  // Total Line
  doc.setLineWidth(0.3);
  doc.line(summaryX, finalY + 16, pageWidth - 15, finalY + 16);
  
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('Grand Total:', summaryX, finalY + 24);
  doc.text(`₹${saleData.total.toFixed(2)}`, pageWidth - 20, finalY + 24, { align: 'right' });
  
  // Footer
  const footerY = doc.internal.pageSize.getHeight() - 30;
  doc.setFontSize(10);
  doc.setFont('helvetica', 'italic');
  doc.text('Thank you for your business!', pageWidth / 2, footerY, { align: 'center' });
  
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.text('This is a computer-generated invoice and does not require a signature.', pageWidth / 2, footerY + 6, { align: 'center' });
  
  // Save the PDF
  doc.save(`invoice_${invoiceNumber}.pdf`);
};

export default generateInvoicePDF;