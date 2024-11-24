import streamlit as st #Web sitesindeki ayarlamaları ve tasarımları oluşturmaya yarar.

import plotly.express as px # seaborn kütüphanesi yerine bu kütüphaneyi kullanıyoruz web sitesi için,interaktif görseller oluşturmayı sağlar.

import pandas as pd
import os #opretaing system
import matplotlib.pyplot as plt



#Streamlit sayfası için yapılandırma ayarlarını yükleyeceğiz
st.set_page_config('SuperStore!!!',page_icon='bar_chart',layout='wide')

#uygulama başlığını belirtelim
st.title('Örnek Bir SuperStore EDA Analizi')

#Sayfanın üst kısmında boşluk miktarını artırmak için css stili ekleyelim

st.markdown("<style>div.block-container{padding-top:2rem;}</style>)",unsafe_allow_html=True)
#Kullanıcıya dosya yükleme seçeneği sunacağız
f1 = st.file_uploader('Dosya Klasörü: Dosyayı Yükle',type=(['csv','txt','xlsx','xls']))
                                                            

if f1 is not None:
   filename = f1.name # Yüklenen dosyanın adını aldık
   st.write(filename) # dosyanın ismini ekrana yazdırdık
   pd.read_csv(filename,encoding='utf-8') # yüklenen dosyayı csv olarak okuduk
else:
    # Eğer kullanıcı dosya yüklemediyse yerel dosyadaki SuperStore.csv dosyasını alacağız ve onu okuyacağız.
    os.chdir('/workspaces/SupeStore_Analysis_Project') # bulunduğumuz dizini Superstore.csv klasörünün içinde olduğumuzdan emin olmak için yazdık
    df = pd.read_csv('Superstore.csv',encoding = 'utf-8')


 #Sayfa düzenini 2 sütun olarak ayarlıyoruz
col1,col2 = st.columns(2)

#Order Date sütununu tarih formatına çevirdik
df['Order Date']    = pd.to_datetime(df['Order Date'])

#verilerin başladığı ve bittiği tarihler arasındaki aralığı hesaplıyoruz
baslangic_tarih = pd.to_datetime(['Order Date']).min()
bitis_tarih = pd.to_datetime(df['Order Date']).max()

#kullanıcıdan başlangıç ve bitiş tarihlerini alıyoruz
with col1: # web sitesinin sol kısmına yapmak istediğimiz işlemi with bloğunda yazıcaz
    tarih1 = pd.to_datetime(st.date_input('Sipariş başlangıç tarih,baslangic_tarih')) # kullanıcının seçmesi için başlangıç tarihi girdik

with col2:
    tarih2 = pd.to_datetime(st.date_input('Sipariş bitiş tarih',bitis_tarih)) #kullanıcının sipariş bitiş tarihini girmesini istedik    


#Kullanıcının seçtiği tarihleri kısıtlayalım
df = df[(df['Order Date'] >= tarih1) & (df['Order Date'] <= tarih2)].copy() # hiçbir zaman orjinal veri setini değiştirmiyoruz kopyalarla çalışıyoruz.İşlemleri sıfırladığımız zaman orjinal veri setine dönebilmek için


#kenar çubuğu ekleyelim
st.sidebar.header('Filtreni Seç')

#bölge seçeneği ekleyelim kullanıcı bir veya birden fazla bölge seçebilir.
bölge = st.sidebar.multiselect('Bölgeni Seç', df['Region'].unigue()) # tüm bölgeleri göstermesini sağladık.

if not bölge:
    df2 = df.copy() #veri setinin tamamını kullanıyorum ama orjinal veri setine dokunmadan kopyasıyla işlem yapıyoruz
else:
    df2 = df[df['Region'].isin(bölge)]

#bölge seçeneği ekleyelim kullanıcı bir veya birden fazla bölge seçebilir.
bölge = st.sidebar.multiselect('Bölgeni Seç', df['Region'].unigue()) # tüm bölgeleri göstermesini sağladık.

# eyalet seçeneği ekleyelim kullanıcı bir ya da birden fazla eyalet seçebilir.
eyalet = st.sidebar.multiselect('Eyaletini Seç', df2['State'].unique()) # Tüm eyaletleri 1 kere görüntülemesini sağladuk

if not eyalet:
    df3 = df2.copy() 
else:
    df3 = df2[df2['State'].isin(eyalet)]

#Şehir Filtresi Seçelim
sehir = st.sidebar.multiselect('Şehiri Seç', df3['City'].unique()) # birden fazla şehir seçebilir

#Kullanıcının Datanın Seçip Kaldırma Durumuna Göre Kombinasyonlarını Ekleyelim
if not bölge and not eyalet and not sehir:
    filtreli_df = df # Sadece tarih aralığı seçtiği kopya df'e eşitledik
#Sadece Bölge Seçebilir
elif not eyalet and not sehir:
    filtreli_df = df[df['Region'].isin(bölge)] # Sadece tarih aralığı seçtiği kopya df'e eşitledik ve onun içindeki kullanıcın seçmiş olduğu bölgeleri aldık
#hem eyalet hem sehir secebilir    
elif eyalet and sehir: 
    filtreli_df =  df3[df['State'].isin(eyalet) & df3['City'].isin(sehir)] # Kullanıcın filtrelemek istediği eyaletleri filtrelenmemiş DataFrame içerisinden alıyorum ve filtrelemek istediği şehirleri filtrelenmiş eyaletler olan DataFrame içerisinden alıyorum
#hem bölge hem şehir seçebilir
elif bölge and sehir:
    filtreli_df = df3[df['Region'].isin(bölge) & df3['City'].isin(sehir)]
#hem bölge hem eyalet
elif bölge and eyalet:
    filtreli_df = df3[df['Region'].isin(bölge) & df3['State'].isin(eyalet)]
#sadece şehir filtreleyebilir
elif sehir:
    filtreli_df = df3[df3['City'].isin(sehir)]
else:
    # Hepsini Filtreleyebilir
    filtreli_df = df3[df3['Region'].isin(bölge) & df3['State'].isin(eyalet) & df3['City'].isin(sehir)]

category_df = filtreli_df.groupby(by = ['Category'], as_index = False)['Sales'].min() 

#görselleştirmelere başlayalım
with col1:
    st.subheader('Category Wise Sales')
    fig = px.bar(category_df, x = 'Category', y = 'Sales', text = ['${:,.2f}'.format(x) for x in category_df['Sales']])
    st.plotly_chart(fig, height = 200,use_container_width=True)
with col2:
    st.subheader('Region Wise Sales')
    fig = px.pie(filtered_df,values = 'Sales',names = 'Region', hole = 0.5)
    fig.update_traces(text = filtered_df['Region'], textposition = 'outside')
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))

with cl1:
    with st.expander('Kategorik Veri Seti'):
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button('Datayı İndir',data = csv, file_name = 'Category.csv',mime = 'txt/csv',
                           help = 'Csv Dosyayı İndirmek İçin Buraya Tıklayın')

with cl2:
    with st.expander('Bölgesel Veri Seti'):
        region = filtered_df.groupby(by = 'Region',as_index = False)['Sales'].sum()
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button('Datayı İndir',data = csv, file_name = 'Region.csv',mime = 'txt/csv',
                           help = 'Csv Dosyayı İndirmek İçin Buraya Tıklayın')


filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M') # Satışların ay bazlı analizini yapacağız Order Date içerisinden sadece ayları seçtin
linechart = pd.DataFrame(filtered_df.groupby(by=filtered_df['month_year'].dt.strftime("%Y : %B"))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x='month_year', y ='Sales', labels = {'Sales': 'Amount'}, height = 500, width = 1000, template = 'gridon')
st.plotly_chart(fig2, use_container_width=True) # Kullanıcak alanı ölçeklendirmeye izin verir.

with st.expander('Time Series Datayı Görüntüle'):
    st.write(linechart.T.style.background_gradient(cmap = 'Blue'))
    csv = linechart.to_csv(index =False).encode('utf-8')
    st.download_button('Dowloand Button', data = csv, file_name = 'TimeSeries.csv',mime = 'text/csv')


st.subheader('Satışları Gösteren Hiyeraşik Görselleştirme')
fig3 = px.treemap(filtered_df, path = ['Region','Category','Sub-Category'], values = 'Sales', color = 'Sub-Category')
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width = True)

col1, col2 = st.columns((2))

with chart:
    st.subheader('Müşteri Segmentine Göre Satışlar')
    fig = px.pie(filtered_df, values = 'Sales', names = 'Segment', template = 'plotly_dark')
    fig.update_traces(text = filtered_df['Segment'], textposition='inside') # Görsel üzerine yazacığımız metni belirliyor
    st.plotly_chart(fig, use_container_width = True)

with chart2:
    st.subheader('Ürün Kategorisene Göre Satışlar')
    fig = px.pie(filtered_df, values = 'Sales', names = 'Category', template = 'plotly_dark')
    fig.update_traces(text = filtered_df['Category'], textposition='inside') # Görsel üzerine yazacığımız metni belirliyor
    st.plotly_chart(fig, use_container_width = True)

import plotly.figure_factory as ff

st.subheader("Ürün Alt Kategorilerin Aylara Göre Satış Özet Tablosu")
with st.expander('Özet Tablo'):
    df_sample = df[0:5][['Region','State','City','Category','Sales','Profit','Quantity']]
    fig = ff.create_table(df_sample, colorscale = 'Cividis')
    st.plotly_chart(fig, use_container_width = True)



#Dağılım Grafikleri Oluşturalım
data1 = px.scatter(filtered_df, x='Sales',y = 'Profit', size = 'Quantity')
data1['layout'].update(title ='Scatter Plot Grafiği Kullanarak Satışlar ve Karlar arasında İlişki Belirleme',
titlefont = dict(size = 20), xaxis = dict(title='Sales', titlefont=dict(size=19)),yaxis = dict(title='Profit', titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)


csv  = df.to_csv(index = False).encode('utf-8')
st.download_button('Datayı İndir',data = csv, file_name = 'Data.csv', mime = 'txt/csv')
                   


                                                            







